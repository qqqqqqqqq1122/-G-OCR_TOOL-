@echo off
chcp 65001
title 公式 OCR 后台助手
echo 正在启动指定 Anaconda 环境...

:: 直接调用 zhuan_yu_yin 环境下的 python.exe 来运行你的脚本
D:\anaconda\envs\zhuan_yu_yin\python.exe "G:\OCR_TOOL\PaddleOCR-VL-1.5.py"

pause