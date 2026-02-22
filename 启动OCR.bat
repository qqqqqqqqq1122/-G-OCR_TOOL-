@echo off
chcp 65001
title 公式 OCR 后台助手

:: 1. 启动 Snipaste
echo 正在为您唤醒 Snipaste 截图神器...
start "" "G:\Snipaste-2.11.3-x64\Snipaste.exe"

:: 2. 启动 OCR 核心脚本
echo 正在启动指定 Anaconda 环境与 OCR 引擎...
D:\anaconda\envs\zhuan_yu_yin\python.exe "G:\OCR_TOOL\ocr_tool.py"