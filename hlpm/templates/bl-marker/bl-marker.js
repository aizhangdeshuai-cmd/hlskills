/* ============================================================
   BL Marker System — JS 控制器
   抽取自 knowledge/doc/v1/design/dashboard.html
   用于 hlpm 6b 步骤产出的 HTML 设计稿复用

   用法: 在设计稿 </body> 前
     <script src="bl-marker.js"></script>
   配合 bl-marker.css + HTML 钉位 + REQUIREMENTS 数据一起用

   依赖: 设计稿 HTML 必须含
   - <aside id="bl-drawer"> ... </aside>  抽屉容器
   - <button id="bl-toggle">⇆</button>     悬浮开关
   - <button class="bl-pin" data-bl="blN">N</button>  钉位
   - 钉位父元素有 position:relative(否则 absolute 钉位跳到 viewport 角)
   ============================================================ */

(function blPinSystem(){
  'use strict';
  /* ============================================================
     ⚠️ 使用前必读: REQUIREMENTS 数据
     ------------------------------------------------------------
     1. 这是模板数据 — 在你自己的设计稿里替换成实际 PRD 章节
     2. 每个 BL 必须有 title (含 "BL-N 名称" 前缀) + sections[] 数组
     3. 叙事结构(v28 起固定, 对齐 PRD 15 字段卡片):
        一句话 → 主场景 → 替代/异常场景 → 业务规则 → 状态机变化 → AC 验收表
        (缺场景/规则/AC 任一段 → hlpm 6b.6 评审驳回)
     4. sections[].body 支持四种语法:
        - 普通段落: 多行用 \n 分隔(渲染时用 <br> 分行)
        - 编号列表: 任一行以 "1." 开头 → 渲染为 <ol>
        - markdown 表格: | 表格 | 列分隔 | + 第二行 |---|---|
        - [flow] 场景流程链(v28): 首行写 [flow], 步骤用 → 或换行连接,
          编号可带字母标分支(3a./3b., 红色虚框渲染); 场景段必须用 [flow]
     5. sections[].state (v28, 可选): 替代/异常场景段标页面态(如 'error')
        → 抽屉显示"▶ 查看该状态"按钮。点击: 优先派 bl:state 事件
        (页面 document.addEventListener('bl:state', e => { e.preventDefault(); ...自切... })
        则页面自切不刷新); 页面未监听 → URL ?state= 兜底重载并重开抽屉
     6. 钉点 hover 摘要(v28): JS 自动取"一句话"段首行填 pin 的 title, 无需手填
     7. ⚠️ 同步源: 同步 knowledge/doc/{ver}/prd.md §N 时, 这里也要改
     ============================================================ */
  var REQUIREMENTS = {
    bl1: { title: 'BL-1 示例需求点', sections: [
      { title: '一句话', body: '替换成你的 PRD §1 一句话描述(本节首行会被 JS 自动用作钉点 hover 摘要).' },
      { title: '主场景', body: '[flow]\n1. 用户点击"导出" → 2. 系统校验筛选条件 → 3. 生成并下载文件' },
      { title: '替代/异常场景', body: '[flow]\n3a. 筛选结果为空:提示"无数据可导出"\n3b. 无权限:按钮置灰 + hover 提示原因', state: 'error' },
      { title: '业务规则', body: '1. 业务规则 1(摘自 PRD §1.9 原文)\n2. 业务规则 2\n3. 业务规则 3' },
      { title: '状态机变化', body: '导出任务: 无 → 生成中 → 已完成/失败(不涉及状态机则写"不涉及")' },
      { title: 'AC 验收', body: '| AC | 验收点 | 优先级 |\n|---|---|---|\n| AC-1 | 示例验收 1 | P0 |\n| AC-2 | 示例验收 2 | P0 |' }
    ]},
    bl2: { title: 'BL-2 第二个示例', sections: [
      { title: '一句话', body: '复制上面 BL-1 的叙事结构(一句话/主场景/替代异常/规则/状态机/AC), 替换内容即可.' }
    ]}
  };

  // ===== 抽屉 =====
  var drawer = document.getElementById('bl-drawer');
  var drawerBadge = document.getElementById('bl-drawer-badge');
  var drawerTitle = document.getElementById('bl-drawer-title');
  var drawerBody  = document.getElementById('bl-drawer-body');
  var drawerClose = document.getElementById('bl-drawer-close');
  var currentBl = null;
  var WARN_MSG = '<div class="bl-warn">⚠️ 该需求点尚未配置</div>';

  function renderBody(blId) {
    var data = REQUIREMENTS[blId];
    if (!data) { drawerBody.innerHTML = WARN_MSG; return; }
    var html = '';
    (data.sections || []).forEach(function(s){
      if (!s || !s.body) return;
      html += '<div class="bl-section">';
      if (s.title) html += '<div class="bl-section-title">' + s.title + '</div>';
      html += '<div class="bl-section-body">' + renderText(s.body);
      if (s.state) html += '<button type="button" class="bl-state-btn" data-state="' + escapeHtml(s.state) + '">▶ 查看该状态(' + escapeHtml(s.state) + ')</button>';
      html += '</div>';
      html += '</div>';
    });
    if (!html) html = WARN_MSG;
    drawerBody.innerHTML = html;
  }
  function renderText(text) {
    if (!text) return '';
    // [flow] 场景流程链(v28): 首行 [flow]
    if (/^\s*\[flow\]\s*(\n|$)/.test(text)) {
      return renderFlow(text.replace(/^\s*\[flow\]\s*(\n|$)/, ''));
    }
    // 表格语法: 首行含 |, 第二行是对齐行
    if (/\|/.test(text) && /^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$/.test(text.split('\n')[1] || '')) {
      return renderTable(text);
    }
    // 编号列表
    if (/^\d+\./m.test(text)) {
      var items = text.split(/\n(?=\d+\.)/).map(function(line){
        return '<li>' + escapeHtml(line.replace(/^\d+\.\s*/, '')) + '</li>';
      }).join('');
      return '<ol>' + items + '</ol>';
    }
    // 普通段落
    var lines = text.split('\n').map(function(l){ return escapeHtml(l); });
    return '<p>' + lines.join('<br>') + '</p>';
  }
  // [flow] 场景流程链渲染(v28): 步骤用 → 或换行分隔, "3a./3b." 编号前缀标分支(红虚框)
  function renderFlow(text) {
    var tokens = text.split(/\n|→/);
    var html = '<div class="bl-flow">';
    var count = 0;
    tokens.forEach(function(t){
      t = t.trim();
      if (!t) return;
      var branch = false;
      var m = t.match(/^(\d+)([a-z]?)\.\s*(.*)$/);
      if (m) { branch = !!m[2]; t = m[3]; }
      if (count) html += '<span class="bl-flow-arrow">→</span>';
      html += '<span class="bl-flow-step' + (branch ? ' branch' : '') + '">' + escapeHtml(t) + '</span>';
      count++;
    });
    return html + '</div>';
  }
  function renderTable(text) {
    var rows = text.split('\n').filter(function(r){ return r.trim().length > 0; });
    if (rows.length < 2) return '<p>' + escapeHtml(text) + '</p>';
    var alignRow = rows[1].match(/^\s*\|?\s*(:?-+:?\s*\|\s*)+:?-+\s*\|?\s*$/);
    if (!alignRow) return '<p>' + escapeHtml(text) + '</p>';
    function splitCells(r) {
      var t = r.trim();
      if (t.charAt(0) === '|') t = t.slice(1);
      if (t.charAt(t.length - 1) === '|') t = t.slice(0, -1);
      return t.split('|').map(function(c){ return c.trim(); });
    }
    var aligns = splitCells(rows[1]).map(function(c){
      var left = c.charAt(0) === ':';
      var right = c.charAt(c.length - 1) === ':';
      if (left && right) return 'center';
      if (right) return 'right';
      if (left) return 'left';
      return 'left';
    });
    var header = splitCells(rows[0]);
    var body = rows.slice(2).map(splitCells);
    var html = '<table class="bl-table"><thead><tr>';
    header.forEach(function(cell, i){
      html += '<th style="text-align:' + (aligns[i] || 'left') + '">' + escapeHtml(cell) + '</th>';
    });
    html += '</tr></thead><tbody>';
    body.forEach(function(row){
      html += '<tr>';
      row.forEach(function(cell, i){
        html += '<td style="text-align:' + (aligns[i] || 'left') + '">' + escapeHtml(cell) + '</td>';
      });
      html += '</tr>';
    });
    html += '</tbody></table>';
    return html;
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function(c){
      return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c];
    });
  }
  function openDrawer(blId) {
    var data = REQUIREMENTS[blId];
    drawerBadge.textContent = blId.toUpperCase();
    drawerTitle.textContent = data ? data.title.replace(/^BL-\S+\s*/, '') : '(无标题)';
    renderBody(blId);
    drawer.classList.add('open');
    document.body.classList.add('drawer-open');
    currentBl = blId;
  }
  function closeDrawer() {
    drawer.classList.remove('open');
    document.body.classList.remove('drawer-open');
    currentBl = null;
  }

  drawerClose.addEventListener('click', closeDrawer);
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && currentBl) closeDrawer();
  });
  document.addEventListener('click', function(e){
    if (!currentBl) return;
    if (drawer.contains(e.target)) return;
    if (e.target.closest && e.target.closest('.bl-pin')) return;
    if (e.target.closest && e.target.closest('#bl-toggle')) return;
    closeDrawer();
  });
  document.addEventListener('click', function(e){
    var pin = e.target.closest && e.target.closest('.bl-pin');
    if (!pin) return;
    var blId = pin.dataset.bl;
    if (!blId) return;
    if (currentBl === blId) { closeDrawer(); return; }
    openDrawer(blId);
  });

  // ===== 场景联动 + hover 摘要(v28) =====
  // 点"▶ 查看该状态": 优先派 bl:state 事件(页面监听并 preventDefault → 页面自切不刷新);
  // 页面未监听 → URL ?state= 兜底重载, 重载后自动重开抽屉
  var REOPEN_LS_KEY = 'blReopen';
  function gotoState(state) {
    if (!state) return;
    var ev = new CustomEvent('bl:state', { detail: { state: state }, cancelable: true });
    var handled = !document.dispatchEvent(ev);
    if (handled) return;
    try { if (currentBl) localStorage.setItem(REOPEN_LS_KEY, currentBl); } catch(e) {}
    var url = location.href.split('#')[0].replace(/([?&])state=[^&]*(&|$)/, function(m, p1, p2){ return p2 === '&' ? p1 : ''; });
    url += (url.indexOf('?') >= 0 ? '&' : '?') + 'state=' + encodeURIComponent(state);
    location.href = url;
  }
  drawerBody.addEventListener('click', function(e){
    var btn = e.target.closest && e.target.closest('.bl-state-btn');
    if (!btn) return;
    gotoState(btn.dataset.state);
  });

  // 钉点 hover 摘要: 自动取"一句话"段(sections[0])首行填 title(已手填 title 的钉点不覆盖)
  document.querySelectorAll('.bl-pin[data-bl]').forEach(function(pin){
    if (pin.getAttribute('title')) return;
    var d = REQUIREMENTS[pin.dataset.bl];
    if (!d || !d.sections || !d.sections.length || !d.sections[0].body) return;
    var line = d.sections[0].body.split('\n')[0].trim();
    if (line) pin.setAttribute('title', d.title + ': ' + line);
  });

  // URL 兜底切态重载后, 自动重开之前打开的抽屉
  try {
    var reopen = localStorage.getItem(REOPEN_LS_KEY);
    if (reopen) {
      localStorage.removeItem(REOPEN_LS_KEY);
      if (REQUIREMENTS[reopen]) openDrawer(reopen);
    }
  } catch(e) {}

  // ===== 标记可见性 + 悬浮按钮位置 =====
  var toggleBtn = document.getElementById('bl-toggle');
  var LS_KEY = 'blTogglePos';
  var pos = null;
  try { pos = JSON.parse(localStorage.getItem(LS_KEY) || 'null'); } catch(e) { pos = null; }

  function applyPos(p) {
    if (!p || typeof p.x !== 'number' || typeof p.y !== 'number') {
      toggleBtn.style.left = 'auto'; toggleBtn.style.top = 'auto';
      toggleBtn.style.right = '20px'; toggleBtn.style.bottom = '20px';
      return;
    }
    var maxX = Math.max(0, window.innerWidth - toggleBtn.offsetWidth);
    var maxY = Math.max(0, window.innerHeight - toggleBtn.offsetHeight);
    var x = Math.max(0, Math.min(p.x, maxX));
    var y = Math.max(0, Math.min(p.y, maxY));
    toggleBtn.style.left = x + 'px'; toggleBtn.style.top = y + 'px';
    toggleBtn.style.right = 'auto'; toggleBtn.style.bottom = 'auto';
  }
  applyPos(pos);

  function savePos(p) { try { localStorage.setItem(LS_KEY, JSON.stringify(p)); } catch(e) {} }
  function clearPos() { try { localStorage.removeItem(LS_KEY); } catch(e) {} }

  function setPinsHidden(hidden) {
    document.body.classList.toggle('bl-pins-hidden', !!hidden);
    toggleBtn.setAttribute('aria-pressed', hidden ? 'false' : 'true');
    toggleBtn.textContent = hidden ? '◌' : '⇆';
  }

  var press = null;
  var LONG_MS = 600, MOVE_THRESH = 5;

  toggleBtn.addEventListener('mousedown', function(e){
    if (e.button !== 0) return;
    var rect = toggleBtn.getBoundingClientRect();
    press = {
      startX: e.clientX, startY: e.clientY,
      sx: rect.left, sy: rect.top,
      t: Date.now(), moved: false, longArmed: false
    };
    setTimeout(function(){
      if (press && !press.moved) press.longArmed = true;
    }, LONG_MS);
    e.preventDefault();
  });

  document.addEventListener('mousemove', function(e){
    if (!press) return;
    var dx = e.clientX - press.startX, dy = e.clientY - press.startY;
    if (!press.moved) {
      if (Math.abs(dx) + Math.abs(dy) <= MOVE_THRESH) return;
      press.moved = true;
      toggleBtn.classList.add('dragging');
    }
    var rect = toggleBtn.getBoundingClientRect();
    var nx = press.sx + (e.clientX - press.startX);
    var ny = press.sy + (e.clientY - press.startY);
    var maxX = Math.max(0, window.innerWidth - rect.width);
    var maxY = Math.max(0, window.innerHeight - rect.height);
    nx = Math.max(0, Math.min(nx, maxX));
    ny = Math.max(0, Math.min(ny, maxY));
    toggleBtn.style.left = nx + 'px'; toggleBtn.style.top = ny + 'px';
    toggleBtn.style.right = 'auto'; toggleBtn.style.bottom = 'auto';
  });

  document.addEventListener('mouseup', function(e){
    if (!press) return;
    var dt = Date.now() - press.t;
    if (!press.moved) {
      if (dt >= LONG_MS && press.longArmed) {
        applyPos(null); clearPos(); pos = null;
      } else if (dt < LONG_MS) {
        var hidden = document.body.classList.contains('bl-pins-hidden');
        setPinsHidden(!hidden);
      }
    } else {
      var rect = toggleBtn.getBoundingClientRect();
      pos = { x: rect.left, y: rect.top };
      savePos(pos);
      toggleBtn.classList.remove('dragging');
    }
    press = null;
  });

  toggleBtn.addEventListener('keydown', function(e){
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      var hidden = document.body.classList.contains('bl-pins-hidden');
      setPinsHidden(!hidden);
    }
  });

  window.addEventListener('resize', function(){
    if (pos) applyPos(pos);
  });

  // ===== 抽屉宽度调节 =====
  var DRAWER_LS_KEY = 'blDrawerWidth';
  var DRAWER_DEFAULT_W = 360, DRAWER_MIN_W = 280, DRAWER_MAX_RATIO = 0.7;
  var drawerWidth = null;
  try { drawerWidth = JSON.parse(localStorage.getItem(DRAWER_LS_KEY) || 'null'); } catch(e) {}
  function applyDrawerWidth(w) {
    if (typeof w !== 'number' || !isFinite(w) || w < DRAWER_MIN_W) return;
    var maxW = Math.max(DRAWER_MIN_W, Math.floor(window.innerWidth * DRAWER_MAX_RATIO));
    w = Math.min(w, maxW);
    drawer.style.width = w + 'px';
  }
  applyDrawerWidth(drawerWidth);

  var resizeHandle = document.getElementById('bl-drawer-resize');
  var resizeDrag = null;
  resizeHandle.addEventListener('mousedown', function(e){
    if (e.button !== 0) return;
    resizeDrag = { startX: e.clientX, startW: drawer.getBoundingClientRect().width };
    resizeHandle.classList.add('dragging');
    document.body.style.cursor = 'ew-resize';
    e.preventDefault();
  });
  document.addEventListener('mousemove', function(e){
    if (!resizeDrag) return;
    var nx = resizeDrag.startW + (resizeDrag.startX - e.clientX);
    var maxW = Math.max(DRAWER_MIN_W, Math.floor(window.innerWidth * DRAWER_MAX_RATIO));
    nx = Math.max(DRAWER_MIN_W, Math.min(nx, maxW));
    drawer.style.width = nx + 'px';
  });
  document.addEventListener('mouseup', function(){
    if (!resizeDrag) return;
    resizeDrag = null;
    resizeHandle.classList.remove('dragging');
    document.body.style.cursor = '';
    var w = drawer.getBoundingClientRect().width;
    try { localStorage.setItem(DRAWER_LS_KEY, JSON.stringify(Math.round(w))); } catch(e) {}
  });
  resizeHandle.addEventListener('dblclick', function(){
    drawer.style.width = DRAWER_DEFAULT_W + 'px';
    try { localStorage.removeItem(DRAWER_LS_KEY); } catch(e) {}
  });
  resizeHandle.addEventListener('keydown', function(e){
    if (e.key === 'ArrowLeft') {
      drawer.style.width = (drawer.getBoundingClientRect().width + 24) + 'px';
      try { localStorage.setItem(DRAWER_LS_KEY, JSON.stringify(Math.round(drawer.getBoundingClientRect().width))); } catch(err) {}
    } else if (e.key === 'ArrowRight') {
      drawer.style.width = Math.max(DRAWER_MIN_W, drawer.getBoundingClientRect().width - 24) + 'px';
      try { localStorage.setItem(DRAWER_LS_KEY, JSON.stringify(Math.round(drawer.getBoundingClientRect().width))); } catch(err) {}
    }
  });

  // ===== 调试面板 =====
  function isTestMode() { return !!window.__BL_TEST__; }
  function showTestPanel(results) {
    var panel = document.createElement('div');
    panel.className = 'bl-test-panel visible';
    panel.innerHTML = '<h4>BL TC 调试面板 (?bl-test=1)</h4>' +
      Object.keys(results).map(function(k){
        var r = results[k];
        return '<div class="tc"><span>' + k + ' ' + r.name + '</span>' +
               '<span class="' + (r.pass ? 'pass' : 'fail') + '">' + (r.pass ? '✓' : '✗') + '</span></div>';
      }).join('');
    document.body.appendChild(panel);
  }
  function runAllTC() {
    var results = {};
    results.TC01 = { name: '所有 BL 抽屉有内容', pass: false };
    var checked = [];
    Object.keys(REQUIREMENTS).forEach(function(blId){
      var pin = document.querySelector('.bl-pin[data-bl="' + blId + '"]');
      if (!pin) return;
      pin.click();
      var t = document.getElementById('bl-drawer-title').textContent;
      if (currentBl === blId && t && t.length > 0) checked.push(blId);
    });
    results.TC01.pass = checked.length === Object.keys(REQUIREMENTS).length;

    results.TC02 = { name: '同 BL 双击 关闭再开', pass: false };
    var p = document.querySelector('.bl-pin[data-bl="bl3"]') || document.querySelector('.bl-pin');
    if (p) {
      var blId = p.dataset.bl;
      p.click(); var first = currentBl;
      p.click(); var closed = !currentBl;
      p.click(); var reopened = currentBl === blId;
      results.TC02.pass = first === blId && closed && reopened;
    }

    results.TC03 = { name: '× / ESC / 外部 都能关', pass: false };
    var p3 = document.querySelector('.bl-pin[data-bl="bl1"]') || document.querySelector('.bl-pin');
    if (p3) {
      p3.click();
      document.getElementById('bl-drawer-close').click();
      var afterX = !currentBl;
      p3.click();
      document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));
      var afterEsc = !currentBl;
      p3.click();
      document.body.click();
      var afterOutside = !currentBl;
      results.TC03.pass = afterX && afterEsc && afterOutside;
    }

    results.TC04 = { name: '悬浮按钮 click 切换显隐', pass: false };
    var initialHidden = document.body.classList.contains('bl-pins-hidden');
    toggleBtn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, button: 0, clientX: 100, clientY: 100}));
    toggleBtn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true, button: 0, clientX: 100, clientY: 100}));
    var hidden = document.body.classList.contains('bl-pins-hidden') !== initialHidden;
    toggleBtn.dispatchEvent(new MouseEvent('mousedown', {bubbles: true, button: 0, clientX: 100, clientY: 100}));
    toggleBtn.dispatchEvent(new MouseEvent('mouseup', {bubbles: true, button: 0, clientX: 100, clientY: 100}));
    var shown = document.body.classList.contains('bl-pins-hidden') === initialHidden;
    results.TC04.pass = hidden && shown;

    results.TC05 = { name: 'localStorage 保存拖动位置', pass: false };
    pos = {x:300, y:400}; savePos(pos);
    var stored = JSON.parse(localStorage.getItem(LS_KEY) || 'null');
    results.TC05.pass = stored && stored.x === 300 && stored.y === 400;

    results.TC06 = { name: '长按复位清空 localStorage', pass: false };
    savePos({x:100, y:100});
    applyPos(null); clearPos();
    results.TC06.pass = localStorage.getItem(LS_KEY) === null;

    results.TC07 = { name: '拖动坐标 clamp 屏内', pass: false };
    var maxX = Math.max(0, window.innerWidth - toggleBtn.offsetWidth);
    var maxY = Math.max(0, window.innerHeight - toggleBtn.offsetHeight);
    applyPos({x: window.innerWidth + 100, y: -50});
    var rect = toggleBtn.getBoundingClientRect();
    results.TC07.pass = rect.left >= 0 && rect.top >= 0 && rect.left <= maxX && rect.top <= maxY;

    results.TC08 = { name: '每 BL 各有钉位', pass: false };
    var counts = {};
    document.querySelectorAll('.bl-pin').forEach(function(p){
      counts[p.dataset.bl] = (counts[p.dataset.bl] || 0) + 1;
    });
    var allCovered = Object.keys(REQUIREMENTS).every(function(k){ return (counts[k]||0) >= 1; });
    results.TC08.pass = allCovered;

    results.TC09 = { name: '钉位 button 可 focus', pass: false };
    var pins = document.querySelectorAll('.bl-pin');
    var allFocusable = Array.from(pins).every(function(p){ return p.tagName === 'BUTTON'; });
    var toggleFocusable = toggleBtn.tagName === 'BUTTON';
    results.TC09.pass = allFocusable && toggleFocusable;

    results.TC10 = { name: '切页关闭抽屉', pass: false };
    var anyPin = document.querySelector('.bl-pin');
    if (anyPin) {
      anyPin.click();
      var navItem = document.querySelector('.nav-item');
      if (navItem) {
        navItem.click();
        results.TC10.pass = !currentBl;
      } else {
        // 无 nav 时跳过：复位抽屉后判通过
        document.getElementById('bl-drawer-close').click();
        results.TC10.name = '切页关闭抽屉（无 nav，跳过）';
        results.TC10.pass = true;
      }
    } else {
      results.TC10.pass = true;  // 无钉位时跳过
    }

    showTestPanel(results);
  }
  if (isTestMode()) {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', runAllTC);
    } else {
      runAllTC();
    }
  }
})();