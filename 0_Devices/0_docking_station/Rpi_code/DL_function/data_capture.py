import os
import time
from picamera2 import Picamera2

# 设置图片保存的文件夹路径
folder_path = './train/base'
os.makedirs(folder_path, exist_ok=True)  # 如果文件夹不存在，则创建文件夹

# 初始化 Picamera2
picam2 = Picamera2()

# 配置相机
config = picam2.create_still_configuration()
picam2.configure(config)
picam2.start()

try:
    for i in range(1, 11):  # 拍摄10张图片
        file_name = os.path.join(folder_path, f"1-{i}.jpg")  # 使用 os.path.join 确保路径正确
        picam2.capture_file(file_name)  # 拍摄并保存图片
        print(f"Captured {file_name}")
        time.sleep(1)  # 拍摄间隔1秒
finally:
    picam2.stop()

print("All images captured and saved successfully.")
