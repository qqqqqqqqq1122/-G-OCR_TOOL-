# import keyboard
# from PIL import ImageGrab, Image
# import pyperclip
# from pix2text import Pix2Text

# print("正在初始化 Pix2Text... (首次运行会自动下载预训练模型，请保持网络通畅)")
# p2t = Pix2Text.from_config()
# print("加载完毕！准备就绪。")

# def recognize_shortcut():
#     # 抓取剪贴板内容
#     img = ImageGrab.grabclipboard()
    
#     if img is None:
#         print("剪贴板中未检测到图片，请先截图。")
#         return
        
#     # 核心修复逻辑：判断剪贴板返回的是否为列表（文件路径）
#     if isinstance(img, list):
#         try:
#             # 如果是列表，读取列表里的第一个文件路径，并将其转换为图片对象
#             img = Image.open(img[0])
#         except Exception as e:
#             print(f"剪贴板中的文件无法作为图片打开: {e}")
#             return

#     print("已获取截图，正在识别文字与公式混合内容...")
#     try:
#         # 调用图文混合识别接口，并要求直接返回文本格式
#         outs = p2t.recognize_text_formula(img, return_text=True)
        
#         # 兼容处理：确保把识别结果提取为纯文本字符串
#         if isinstance(outs, str):
#             res = outs
#         elif isinstance(outs, dict):
#             res = outs.get('text', str(outs))
#         else:
#             # 如果返回的是列表（多行内容），则将它们拼接起来
#             res = "\n".join([item.get('text', '') for item in outs if isinstance(item, dict)])
        
#         # 将识别出的内容自动写入剪贴板
#         pyperclip.copy(res)
#         print(f"识别成功！代码已复制:\n{res}\n")
#     except Exception as e:
#         print(f"识别过程中出现致命错误: {e}")

# # 绑定快捷键 F4
# keyboard.add_hotkey('f4', recognize_shortcut)
# print("【运行中】请用 Win + Shift + S 截图，然后按 F4 进行识别。按 ESC 退出程序。")

# # 保持程序在后台运行，直到按下 ESC 键
# keyboard.wait('esc')

import keyboard
from PIL import ImageGrab, Image
import pyperclip
from pix2text import Pix2Text
import gc  # <--- 新增这行，Python 的垃圾回收

import os

import time
# 👇 === 把下面这段新增的“死亡钩子”复制到你的 import 区域下方 === 👇
import ctypes
import atexit

def clean_up_snipaste():
    """清理函数：静默击杀 Snipaste"""
    os.system("taskkill /f /im Snipaste.exe >nul 2>&1")

# 1. 应对好习惯：按下 ESC 正常退出时，自动清理
atexit.register(clean_up_snipaste)

# 2. 应对点击红叉：拦截 Windows 的 CTRL_CLOSE_EVENT (点击X) 暴力关闭信号
def console_ctrl_handler(ctrl_type):
    if ctrl_type == 2:  # 2 代表点击了右上角的 X
        clean_up_snipaste()
    return False

# 必须将其赋值给全局变量，防止被 Python 的垃圾回收器清理掉
win_handler = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)(console_ctrl_handler)
ctypes.windll.kernel32.SetConsoleCtrlHandler(win_handler, True)
# 👆 ========================================================= 👆
print("正在初始化 Pix2Text... (首次运行会自动下载预训练模型，请保持网络通畅)")
p2t = Pix2Text.from_config()
print("加载完毕！准备就绪。")


def recognize_shortcut():
    print("\n[F1 已按下] 正在偷偷观察剪贴板 (最长等待 20 秒)...")
    
    # 【新增】：先把剪贴板里的旧图片顶掉，换成几个字，防止读到上一次截的图
    pyperclip.copy("WAITING")

    # 【新增】：开启循环，最多偷偷看 20 次（也就是 20 秒）
    for _ in range(20):
        time.sleep(1) # 【新增】：每隔 1 秒看一眼
        
        # 抓取剪贴板内容
        img = ImageGrab.grabclipboard()
        
        # 【修改】：如果剪贴板是空的，或者是刚才塞进去的"WAITING"文字，就继续等下一秒
        if img is None or isinstance(img, str):
            continue
            
        if isinstance(img, list):
            try:
                img = Image.open(img[0])
            except Exception as e:
                print(f"剪贴板中的文件无法作为图片打开: {e}")
                return

        # ==========================================
        # 【终极杀手锏：高质量无损放大】
        # 将截图的长宽各放大 2.5 倍，让 AI 看清英文小字的细节！
        new_size = (int(img.width * 2.5), int(img.height * 2.5))
        # 将长宽各放大 3.0 倍
        # new_size = (int(img.width * 3.0), int(img.height * 3.0))
        # 注意：如果你之前没导入 Image 模块的 Resampling，请确保文件开头有 from PIL import Image
        img = img.resize(new_size, Image.Resampling.LANCZOS)
        # ==========================================

        print("已获取截图（并已自动高清放大），正在识别...")
        try:
            # 识别接口（不加 resized_shape，吃满放大后的分辨率）
            outs = p2t.recognize_text_formula(img, return_text=True)
            
            if isinstance(outs, str):
                res = outs
            elif isinstance(outs, dict):
                res = outs.get('text', str(outs))
            else:
                res = "\n".join([item.get('text', '') for item in outs if isinstance(item, dict)])
            
            pyperclip.copy(res)
            print(f"识别成功！代码已复制:\n{res}\n")
        except Exception as e:
            print(f"识别过程中出现致命错误: {e}")
        finally:
            # 1. 强制关闭 PIL 图片底层的 C 语言对象释放内存
            if 'img' in locals() and hasattr(img, 'close'):
                img.close()
                
            # 2. 删除巨大的图片变量
            if 'img' in locals():
                del img 
                
            # 3. 挥起皮鞭，强制 Python 立刻打扫内存垃圾！
            gc.collect()
            print("🧹 [系统提示] 内存与缓存已强制清理完毕。")
            
        # 【新增】：一旦成功识别并清理完毕，立刻退出这个函数，不再偷看剪贴板！
        return 

    # 【新增】：如果 20 秒内你没完成截图复制，自动结束本次等待
    print("⏳ 20秒倒计时结束，未检测到新截图，继续待命。")

# 绑定快捷键 F1
keyboard.add_hotkey('f1', recognize_shortcut)
print("【运行中】请用 F1 截图，截完后复制即可自动识别。按 Ctrl+ESC 退出程序。")

# 保持程序在后台运行，直到按下 Ctrl+ESC 键
keyboard.wait('ctrl+esc')
#如果过了 20 秒你依然没有把截图“复制”到剪贴板，它会非常聪明地选择“放弃并回去睡觉”，绝对不会卡死你的电脑，也不会闪退报错。重新触发：如果你这时候又按下了一次 F1，它就会瞬间再次被唤醒，重新给你开启一个全新的 20 秒侦听倒计时。
# def recognize_shortcut():
    
#     # 抓取剪贴板内容
#     img = ImageGrab.grabclipboard()
    
#     if img is None:
#         print("剪贴板中未检测到图片，请先截图。")
#         return
        
#     if isinstance(img, list):
#         try:
#             img = Image.open(img[0])
#         except Exception as e:
#             print(f"剪贴板中的文件无法作为图片打开: {e}")
#             return

#     # ==========================================
#     # 【终极杀手锏：高质量无损放大】
#     # 将截图的长宽各放大 2.5 倍，让 AI 看清英文小字的细节！
#     new_size = (int(img.width * 2.5), int(img.height * 2.5))
#     # 将长宽各放大 3.0 倍
#     # new_size = (int(img.width * 3.0), int(img.height * 3.0))
#     # 注意：如果你之前没导入 Image 模块的 Resampling，请确保文件开头有 from PIL import Image
#     img = img.resize(new_size, Image.Resampling.LANCZOS)
#     # ==========================================

#     print("已获取截图（并已自动高清放大），正在识别...")
#     try:
#         # 识别接口（不加 resized_shape，吃满放大后的分辨率）
#         outs = p2t.recognize_text_formula(img, return_text=True)
        
#         if isinstance(outs, str):
#             res = outs
#         elif isinstance(outs, dict):
#             res = outs.get('text', str(outs))
#         else:
#             res = "\n".join([item.get('text', '') for item in outs if isinstance(item, dict)])
        
#         pyperclip.copy(res)
#         print(f"识别成功！代码已复制:\n{res}\n")
#     except Exception as e:
#         print(f"识别过程中出现致命错误: {e}")
#     finally:
#         # 1. 强制关闭 PIL 图片底层的 C 语言对象释放内存
#         if 'img' in locals() and hasattr(img, 'close'):
#             img.close()
            
#         # 2. 删除巨大的图片变量
#         if 'img' in locals():
#             del img 
            
#         # 3. 挥起皮鞭，强制 Python 立刻打扫内存垃圾！
#         gc.collect()
#         print("🧹 [系统提示] 内存与缓存已强制清理完毕。")

# # 绑定快捷键 F4
# keyboard.add_hotkey('f1', recognize_shortcut)
# print("【运行中】请用 F1 截图，然后按 F4 进行识别。按 ESC 退出程序。")

# # 保持程序在后台运行，直到按下 ESC 键
# keyboard.wait('ctrl+esc')
