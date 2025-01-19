import win32api
import win32con
import win32file
import time
import shutil
import os
import toml
from datetime import datetime
import logging

# 新建ConfigReader类
class ConfigReader:
    def __init__(self, config_path):
        self.config_path = config_path
        self.config = self.read_config()
        self.save_path = self.validate_save_path()
        self.file_extensions = self.get_file_extensions()

    def read_config(self):
        with open(self.config_path, 'r', encoding='utf-8') as file:  # 修改: 指定文件编码为utf-8
            return toml.load(file)

    def validate_save_path(self):
        base_save_path = self.config['Base_options']['save_path']
        # 确保路径中的反斜杠被正确处理
        base_save_path = base_save_path.encode('unicode_escape').decode('utf-8')
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        new_save_path = os.path.join(base_save_path, f'save-path-{timestamp}')
        os.makedirs(new_save_path, exist_ok=True)  # 确保目录存在
        return new_save_path

    def save_actual_save_path(self, source_file, target_file):
        with open('actual_save_path.txt', 'a') as file:  # 修改: 使用追加模式写入文件
            file.write(f"{source_file} -> {target_file} - {datetime.now()}\n")  # 修改: 添加时间戳

    def get_file_extensions(self):
        return {ext: True for ext in self.config['Base_options']['file_extensions']}


class USBMonitor:
    def __init__(self, target_folder, file_extensions):
        # 初始化目标文件夹和文件扩展名字典
        self.target_folder = target_folder
        self.file_extensions = file_extensions

    def get_removable_drives(self):
        """获取所有可移动设备的盘符"""
        # 获取所有逻辑驱动器字符串
        drives = win32api.GetLogicalDriveStrings()
        # 将盘符字符串拆分为列表
        drives = drives.split("\x00")[:-1]
        removable_drives = []
        # 遍历所有驱动器，检查是否为可移动设备
        for drive in drives:
            if win32file.GetDriveType(drive) == win32file.DRIVE_REMOVABLE:
                removable_drives.append(drive)
        return removable_drives

    def move_specific_files(self, source_drive):
        """将特定后缀的文件从源驱动器复制到目标文件夹"""
        # 如果目标文件夹不存在，则创建它
        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)
        
        # 遍历源驱动器中的所有文件和子文件夹
        for root, _, files in os.walk(source_drive):
            for file in files:
                # 检查文件是否在文件扩展名字典中
                if os.path.splitext(file)[1] in self.file_extensions:
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(self.target_folder, file)
                    # 复制文件到目标文件夹
                    shutil.copy(source_file, target_file)
                    # 记录文件的完整路径和当前时间
                    config_reader.save_actual_save_path(source_file, target_file)
                    logging.info(f"复制文件: {source_file} 到 {target_file}")

    def monitor_usb(self):
        """监控 U盘 的插入和移除"""
        # 获取初始的可移动驱动器列表
        previous_drives = set(self.get_removable_drives())
        logging.info(f"初始 U盘 盘符: {previous_drives}")

        while True:
            # 获取当前的可移动驱动器列表
            current_drives = set(self.get_removable_drives())
            # 计算新插入和移除的驱动器
            new_drives = current_drives - previous_drives
            removed_drives = previous_drives - current_drives

            if new_drives:
                logging.info(f"U盘 插入: {new_drives}")
                # 对每个新插入的驱动器，移动特定文件
                for drive in new_drives:
                    self.move_specific_files(drive)
            if removed_drives:
                logging.info(f"U盘 移除: {removed_drives}")

            # 更新之前的驱动器列表
            previous_drives = current_drives
            # 每隔 1 秒检查一次
            time.sleep(1)

if __name__ == "__main__":
    import sys
    import os

    # 创建日志目录
    log_dir = os.path.join(os.getcwd(), 'log')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建日志文件
    log_time = datetime.now().strftime('%Y%m%d%H%M%S')
    log_file = os.path.join(log_dir, f'log_{log_time}.log')

    # 配置日志记录
    logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')

    # 读取配置文件并验证保存路径
    config_reader = ConfigReader(".\\config.toml")
    actual_save_path = config_reader.validate_save_path()
    config_reader.save_actual_save_path(actual_save_path, actual_save_path)  # 修改: 传递两个相同的参数

    # 创建 USBMonitor 实例并开始监控
    usb_monitor = USBMonitor(actual_save_path, config_reader.file_extensions)
    usb_monitor.monitor_usb()
