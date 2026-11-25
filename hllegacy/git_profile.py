"""从指定 Git 快照统计改动范围，输出可直接存入知识条目的 Markdown。"""
import argparse
from collections import Counter
from datetime import date
from pathlib import Path, PurePosixPath
import statistics
import subprocess
import sys


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode(errors='replace').strip() or 'Git 读取失败')
    return result.stdout


def display(value):
    return str(value).replace('\\', '\\\\').replace('|', r'\|').replace('\n', r'\n').replace('\r', r'\r')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--ref', default='HEAD')
    parser.add_argument('--since', type=date.fromisoformat, required=True)
    parser.add_argument('--until', type=date.fromisoformat, required=True)
    parser.add_argument('--layer', action='append', default=[], metavar='名称=路径',
                        help='按真实源码文件或目录汇总，可重复；路径更具体者优先')
    args = parser.parse_args()
    if args.since > args.until:
        parser.error('时间窗起点晚于终点')
    layers = {}
    for item in args.layer:
        name, sep, raw = item.partition('=')
        path = PurePosixPath(raw)
        if not sep or not name or not raw or path.is_absolute() or '..' in path.parts or path in layers:
            parser.error('--layer 须为 名称=仓内相对路径，同一路径只能归入一层')
        layers[path] = name
    window = [f'--since={args.since}T00:00:00Z', f'--until={args.until}T23:59:59Z']
    try:
        if git(args.root, 'rev-parse', '--show-prefix').strip():
            raise ValueError('--root 须指向所选仓库根目录')
        commit = git(args.root, 'rev-parse', '--verify', '--end-of-options', args.ref + '^{commit}').decode().strip()
        shallow = git(args.root, 'rev-parse', '--is-shallow-repository').strip() == b'true'
        total = int(git(args.root, 'rev-list', '--count', *window, commit, '--'))
        # Two NULs and a literal tag delimit commits, even for unusual filenames.
        raw = git(args.root, 'log', '--no-merges', '--find-renames', '-z',
                  '--format=format:%x00%x00COMMIT:%aN%x00', '--name-only', *window, commit, '--')
    except (OSError, ValueError) as error:
        parser.exit(1, f'无法生成 Git 画像：{error}\n')
    files, authors, directories, layer_counts = Counter(), Counter(), Counter(), Counter()
    sizes = []
    for record in raw.split(b'\0\0COMMIT:')[1:]:
        author, _, names = record.partition(b'\0')
        authors[author.decode(errors='replace')] += 1
        paths = [s.decode(errors='backslashreplace') for s in names.removeprefix(b'\n').split(b'\0') if s]
        sizes.append(len(paths))
        files.update(paths)
    for name, count in files.items():
        path = PurePosixPath(name)
        directories[str(path.parent)] += count
        if layers:
            layer = next((layers[key] for key in (path, *path.parents) if key in layers), '未归类')
            layer_counts[layer] += count

    print(f'Git 提交画像 · {display(args.root.resolve().name)} · {display(args.ref)} · {commit}')
    print(f'\n统计时间窗 {args.since} 至 {args.until}（UTC，含首尾）。按提交者时间筛选，合并提交只计入总量。Git 识别的重命名按目标路径计一次。')
    if shallow:
        print('浅克隆，仅统计本地可见历史。')
    print('\n| 指标 | 值 |\n|---|---:|')
    print(f'| 全部提交 | {total} |\n| 非合并提交 | {len(sizes)} |')
    if not sizes:
        print('\n该范围无非合并提交，平均值、中位数和占比不适用。')
        return
    print(f'| 文件改动次数 | {sum(sizes)} |\n| 单次平均文件数 | {statistics.mean(sizes):.1f} |')
    print(f'| 单次文件数中位数 | {statistics.median(sizes):g} |')
    for label, n in [('单文件提交', sizes.count(1)), ('涉及至少 10 个文件', sum(s >= 10 for s in sizes))]:
        print(f'| {label} | {n}/{len(sizes)}（{n / len(sizes):.1%}） |')
    for title, counts, limit in [('热点文件', files, 10), ('目录', directories, 8),
                                 ('主要作者', authors, 10), ('代码层', layer_counts, len(layer_counts))]:
        if counts:
            print(f'\n| {title} | 次数 |\n|---|---:|')
            for key, n in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))[:limit]:
                print(f'| {display(key)} | {n} |')


if __name__ == '__main__':
    main()
