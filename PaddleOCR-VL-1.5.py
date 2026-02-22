import keyboard
from PIL import ImageGrab, Image
import pyperclip
import requests
import base64
import io

# 你的专属 API Token（请妥善保管）
TOKEN = "dba6f68e9200b54e266db043e0bfe04054cfefc4"
API_URL = "https://o6pbndj1vc52f7a5.aistudio-app.com/layout-parsing"

print("正在连接百度 PaddleOCR-VL 云端大模型...")
print("加载完毕！云端引擎准备就绪。")

def recognize_shortcut():
    # 1. 抓取剪贴板内容
    img = ImageGrab.grabclipboard()
    
    if img is None:
        print("剪贴板中未检测到图片，请先用 Win+Shift+S 截图。")
        return
        
    if isinstance(img, list):
        try:
            img = Image.open(img[0])
        except Exception as e:
            print(f"剪贴板图片读取失败: {e}")
            return

    print("已获取截图，正在呼叫云端超级大模型，请稍候...")
    try:
        # 2. 在内存中将图片直接转为 Base64 编码 (速度极快，不落盘)
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        file_bytes = buffered.getvalue()
        file_data = base64.b64encode(file_bytes).decode("ascii")
        
        # 3. 严格按照官方文档构造请求头和请求体
        headers = {
            "Authorization": f"token {TOKEN}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "file": file_data,
            "fileType": 1,  # 1 代表这是一个图片文件
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
            "useChartRecognition": False
        }
        
        # 4. 发送网络请求
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ 服务器请求失败，状态码: {response.status_code}")
            if response.status_code == 429:
                print("可能是今日免费调用额度已用完，或者并发请求太快。")
            return

        # 5. 精准提取官方 JSON 结构里的 Markdown 文本
        result = response.json().get("result", {})
        layout_results = result.get("layoutParsingResults", [])
        
        if not layout_results:
            print("❌ 服务器返回成功，但没有解析到任何内容。")
            return
            
        # 提取出最核心的文本代码
        res_text = layout_results[0].get("markdown", {}).get("text", "")
        
        if not res_text.strip():
            print("⚠️ 识别结果为空，请确认截图中包含清晰的文字或公式。")
            return
        
        # 6. 自动写入剪贴板
        pyperclip.copy(res_text)
        print("=======================================")
        print(f"🎉 识别成功！极其精准的代码已存入剪贴板:\n{res_text}\n")
        print("=======================================")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ 网络异常，请检查网络连接: {e}")
    except Exception as e:
        print(f"❌ 运行过程中出现错误: {e}")

# 绑定快捷键 F4
keyboard.add_hotkey('f4', recognize_shortcut)
print("【最强云端 OCR 运行中】")
print("操作指南：用 Win + Shift + S 截图，然后按 F4 进行极速识别。按 ESC 退出。")

# 保持程序在后台运行，直到按下 ESC 键
keyboard.wait('esc')