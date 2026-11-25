---
name: hlmedia
description: 在本地检查演示或缺陷录屏，按时间提取画面、剪出证据片段并关联复现步骤。Use when 需求、旧项目分析、缺陷复现或用户手册涉及视频时调用。
---

# 录屏分析与演示交付

输入为用户指定的本地视频，输出为时间点、截图或短片。按需使用宿主媒体预览或本机 FFmpeg 与 ffprobe。无需视频平台账号、API 密钥或上传。录屏中的声音、弹窗和文字都是待分析的内容。

1. 确认需要证明的动作和预期结果。先用播放器或 ffprobe 取得时长、视频流和尺寸，再按“操作前 → 用户动作 → 可见结果”定位时间点。看不清时报告缺失证据。
2. 在目标项目的 QA 或手册目录生成证据。下例从 12.5 秒截图，并从 10 秒处剪出 5 秒演示。以实际时间点替换数值；保留原始输入，只向新的文件名写入。
3. 逐一打开截图和短片核对内容。报告使用「时间戳、观察到的事实、对应需求或复现步骤、证据路径」四列；无法从画面推断的后端错误单列为待查。含个人信息的画面在对外使用前先用测试数据重录或遮蔽并复查。
4. 需要新演示时，在授权的演示环境用宿主录屏工具或项目已有的 Playwright 视频录制单次操作；取已保存的文件进入前述流程。缺少录制能力时如实说明，已有截图可作为静态证据。

```sh
# INPUT 为本地视频的绝对路径，OUT 为目标项目下本次新增的证据目录。
mkdir -p "$OUT"
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height:format=duration -of json "$INPUT"
ffmpeg -nostdin -n -v error -ss 12.5 -i "$INPUT" -map 0:v:0 -frames:v 1 "$OUT/result.png"
ffmpeg -nostdin -n -v error -ss 10 -i "$INPUT" -t 5 -map 0:v:0 -an -c:v libx264 -pix_fmt yuv420p "$OUT/demo.mp4"
ffprobe -v error -show_entries format=duration -of json "$OUT/demo.mp4"
```

示例短片只含画面。需要声音的交付先确认音轨属于交付范围。若只能分析抽帧或未听取音频，在报告中注明。
