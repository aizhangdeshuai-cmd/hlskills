"""Run ordered browser QA steps in a fresh Chromium context."""
import argparse
import difflib
import json
from pathlib import Path
import shlex
import sys
from urllib.parse import urlsplit


def address(target):
    if target == "about:blank" or urlsplit(target).scheme in {"http", "https", "file"}:
        return target
    return Path(target).resolve(strict=True).as_uri()


def navigate(page, target):
    response = page.goto(address(target), wait_until="load")
    if response and response.status >= 400:
        raise ValueError(f"导航失败：HTTP {response.status}")


def screenshot(page, filename, *, full=True):
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=path, type="png", full_page=full,
                    mask=[page.locator("input[type=password]")])
    return str(path)


def annotate(page, filename):
    # Number interactive elements in a temporary overlay, leaving page controls untouched.
    overlay = page.evaluate_handle("""() => {
      const layer = document.createElement('div');
      layer.style.cssText = 'position:absolute;inset:0;pointer-events:none;z-index:2147483647';
      layer.setAttribute('aria-hidden', 'true');
      const shadow = layer.attachShadow({mode: 'open'});
      const controls = document.querySelectorAll(
        'a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=tab]');
      for (const el of controls) {
        const r = el.getBoundingClientRect();
        if (!r.width || !r.height || getComputedStyle(el).visibility !== 'visible') continue;
        const mark = document.createElement('span');
        mark.textContent = String(shadow.childNodes.length + 1);
        mark.style.cssText = 'position:absolute;background:#182e59;color:white;font: bold 14px monospace;padding:1px 4px';
        mark.style.left = (r.left + scrollX) + 'px';
        mark.style.top = (r.top + scrollY) + 'px';
        shadow.append(mark);
      }
      document.documentElement.append(layer);
      return layer;
    }""")
    try:
        return screenshot(page, filename)
    finally:
        overlay.evaluate("layer => layer.remove()")
        overlay.dispose()


VIEWPORTS = (("mobile", 375, 812), ("tablet", 768, 1024), ("desktop", 1280, 720))


def responsive(page, prefix):
    original = page.viewport_size
    paths = []
    try:
        for name, width, height in VIEWPORTS:
            page.set_viewport_size({"width": width, "height": height})
            paths.append(screenshot(page, f"{prefix}-{name}-{width}x{height}.png", full=False))
    finally:
        page.set_viewport_size(original)
    return paths


class Session:
    def __init__(self, page):
        self.page = page
        self.snapshots = {}
        self.errors = []
        self.network = []
        self.observe(page)
        page.context.on("page", self.observe)
        page.context.on("response", lambda res: self.record_request(res.request, res.status))
        page.context.on("requestfailed", lambda req: self.record_request(req, "failed"))

    def record_request(self, request, status):
        url = urlsplit(request.url)
        if url.scheme in {"http", "https"}:
            self.network.append({"method": request.method, "status": status, "path": url.path or "/"})

    def observe(self, page):
        page.on("pageerror", lambda error: self.errors.append(str(error)))
        page.on("console", lambda msg: self.errors.append(msg.text) if msg.type == "error" else None)

    def snapshot(self, selector="body", *, diff=False):
        previous = self.snapshots.get(selector)
        if diff and previous is None:
            raise ValueError("请先在同一范围运行 snapshot 记录本次会话的基准。")
        tree = self.page.locator(selector).aria_snapshot()
        self.snapshots[selector] = tree
        if diff:
            return "\n".join(difflib.unified_diff(previous.splitlines(), tree.splitlines(),
                                                  "before", "after", lineterm=""))
        return tree

    def run(self, words):
        page = self.page
        match words:
            case ["goto", target]:
                navigate(page, target)
            case ["load-html", filename]:
                navigate(page, Path(filename).resolve(strict=True).as_uri())
            case ["url"]:
                return page.url
            case ["tabs"]:
                return [p.url for p in page.context.pages]
            case ["newtab", target]:
                self.page = page.context.new_page()
                navigate(self.page, target)
            case ["tab", number]:
                pages = page.context.pages
                if not number.isdigit() or int(number) >= len(pages):
                    raise ValueError("标签页索引超出范围，从 0 开始")
                self.page = pages[int(number)]
            case ["back"]:
                page.go_back(wait_until="load")
            case ["forward"]:
                page.go_forward(wait_until="load")
            case ["reload"]:
                page.reload(wait_until="load")
            case ["click", selector]:
                page.locator(selector).click()
            case ["dblclick", selector]:
                page.locator(selector).dblclick()
            case ["fill", selector, value]:
                page.locator(selector).fill(value)
            case ["select", selector, value]:
                page.locator(selector).select_option(value)
            case ["hover", selector]:
                page.locator(selector).hover()
            case ["type", value]:
                page.keyboard.type(value)
            case ["press", key]:
                page.keyboard.press(key)
            case ["scroll", selector]:
                page.locator(selector).scroll_into_view_if_needed()
            case ["scroll"]:
                page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
            case ["wait", "--load"]:
                page.wait_for_load_state("load")
            case ["wait", "--networkidle"]:
                page.wait_for_load_state("networkidle")
            case ["wait", selector] | ["visible", selector] | ["is", "visible", selector]:
                page.locator(selector).wait_for(state="visible")
            case ["expect-text", selector, expected]:
                from playwright.sync_api import expect
                expect(page.locator(selector)).to_have_text(expected)
            case ["expect-visible-text", selector, expected]:
                from playwright.sync_api import expect
                visible = page.locator(selector).filter(visible=True)
                expect(visible).to_have_text(expected, use_inner_text=True)
            case ["expect-disabled", selector] | ["expect-enabled", selector] | ["expect-hidden", selector]:
                from playwright.sync_api import expect
                assertion = expect(page.locator(selector))
                if words[0] == "expect-hidden":
                    assertion.to_be_hidden()
                elif words[0] == "expect-disabled":
                    assertion.to_be_disabled()
                else:
                    assertion.to_be_enabled()
            case ["links"]:
                return page.locator("a[href]").evaluate_all(
                    "els => els.map(el => ({text:el.innerText, href:el.getAttribute('href')}))")
            case ["forms"]:
                return page.locator("form").evaluate_all("""els => els.map(el => ({
                  id:el.id, method:el.method, fields:Array.from(el.elements, f => ({name:f.name, type:f.type}))
                }))""")
            case ["text"]:
                return page.locator("body").inner_text()
            case ["text", selector]:
                return page.locator(selector).inner_text()
            case ["css", selector, prop]:
                return page.locator(selector).evaluate("(el, p) => getComputedStyle(el).getPropertyValue(p)", prop)
            case ["snapshot"] | ["accessibility"]:
                return self.snapshot()
            case ["snapshot", "-D"]:
                return self.snapshot(diff=True)
            case ["snapshot", "-s", selector]:
                return self.snapshot(selector)
            case ["snapshot", "-s", selector, "-D"] | ["snapshot", "-D", "-s", selector]:
                return self.snapshot(selector, diff=True)
            case ["snapshot", "-a", "-o", filename]:
                return annotate(page, filename)
            case ["screenshot"] | ["screenshot", "--viewport"]:
                return screenshot(page, "screenshot.png", full=len(words) == 1)
            case ["screenshot", filename]:
                return screenshot(page, filename)
            case ["screenshot", "--viewport", filename]:
                return screenshot(page, filename, full=False)
            case ["screenshot", selector, filename]:
                path = Path(filename)
                path.parent.mkdir(parents=True, exist_ok=True)
                page.locator(selector).screenshot(path=path, type="png", mask=[page.locator("input[type=password]")])
                return str(path)
            case ["pdf", filename]:
                path = Path(filename)
                path.parent.mkdir(parents=True, exist_ok=True)
                page.pdf(path=path, print_background=True, prefer_css_page_size=True)
                return str(path)
            case ["responsive", prefix]:
                return responsive(page, prefix)
            case ["console", "--errors"]:
                return self.errors
            case ["network"]:
                return self.network
            case ["expect-clean"]:
                if self.errors:
                    raise ValueError(f"检测到 {len(self.errors)} 条页面或控制台错误")
            case ["perf"]:
                return page.evaluate("""() => {
                  const n = performance.getEntriesByType('navigation')[0];
                  return n ? {ttfbMs:n.responseStart, domReadyMs:n.domContentLoadedEventEnd,
                              loadMs:n.loadEventEnd} : null;
                }""")
            case _:
                raise ValueError("未知命令或参数个数错误，见 hlbrowse/SKILL.md 的命令表。")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="本地 HTML 路径、file://、http(s) URL 或 about:blank")
    parser.add_argument("steps", nargs="*", help="按顺序执行的命令字符串；省略时逐行读取 stdin")
    parser.add_argument("--headed", action="store_true", help="显示隔离的测试浏览器窗口")
    parser.add_argument("--channel", choices=("chrome", "msedge"), help="使用已安装的浏览器")
    args = parser.parse_args()
    try:
        from playwright.sync_api import Error, sync_playwright
    except ImportError:
        parser.exit(2, "缺少 Python Playwright。请按 hlbrowse/SKILL.md 安装 requirements.txt。\n")

    step = "启动浏览器"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(channel=args.channel, headless=not args.headed,
                                                  chromium_sandbox=True)
            try:
                context = browser.new_context(viewport={"width": 1280, "height": 720})
                context.set_default_timeout(5000)
                context.set_default_navigation_timeout(30000)
                page = context.new_page()
                session = Session(page)
                step = "打开页面"
                navigate(page, args.target)
                for index, line in enumerate(args.steps or sys.stdin, start=1):
                    step = f"第 {index} 条命令"
                    words = shlex.split(line)
                    if not words:
                        continue
                    step += f" ({words[0]})"
                    result = session.run(words)
                    print(str(result) if isinstance(result, str) else
                          "OK" if result is None else json.dumps(result, ensure_ascii=False), flush=True)
            finally:
                browser.close()
    except (Error, ValueError, OSError, AssertionError) as exc:
        parser.exit(1, f"{step}失败：{exc}\n")


if __name__ == "__main__":
    main()
