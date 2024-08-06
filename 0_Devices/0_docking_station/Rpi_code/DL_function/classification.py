import RPi.GPIO as GPIO
from picamera2 import Picamera2
from PIL import Image
import torch
from torchvision import transforms
import torch.nn.functional as F
import time
from rpi_ws281x import PixelStrip, Color
from time import sleep
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import threading
import datetime
import pytz
from datetime import timedelta
import board
import adafruit_dht

dht_device = adafruit_dht.DHT22(board.D26, use_pulseio=False)

# LED 圆环配置
LED_COUNT = 24        # LED 数量
LED_PIN = 18          # GPIO 引脚编号（必须支持 PWM！GPIO 18 是一个好选择）
LED_FREQ_HZ = 800000  # LED 信号频率 (Hz)
LED_DMA = 10          # DMA 通道用于生成信号
LED_BRIGHTNESS = 123  # 设置 LED 最大亮度
LED_INVERT = False    # 当使用 NPN 晶体管电平转换时设置为 True

# 设置GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# 创建 PixelStrip 对象
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

cred = credentials.Certificate('/home/MIA/Downloads/CE_dissertation/python_file/DL/ce-dissertation-firebase-adminsdk-ouunw-9e48649dc4.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://ce-dissertation-default-rtdb.europe-west1.firebasedatabase.app/'
    })

def green_breathing_effect(duration=5):
    """显示绿色呼吸灯效果持续指定秒数"""
    start_time = time.time()
    while (time.time() - start_time) < duration:
        for brightness in range(0, 255, 5):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(0, brightness, 0))
            strip.show()
            time.sleep(0.01)
        for brightness in range(255, 0, -5):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(0, brightness, 0))
            strip.show()
            time.sleep(0.01)
    # 灭掉所有 LED
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def red_breathing_effect(duration=5):
    """显示红色呼吸灯效果持续指定秒数"""
    start_time = time.time()
    while (time.time() - start_time) < duration:
        for brightness in range(0, 255, 5):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(brightness, 0, 0))
            strip.show()
            time.sleep(0.01)
        for brightness in range(255, 0, -5):
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(brightness, 0, 0))
            strip.show()
            time.sleep(0.01)
    # 灭掉所有 LED
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)

def rainbowCycle(strip, wait_ms=20, iterations=5, timeout_sec=10):
    """Draw rainbow that uniformly distributes itself across all LEDs."""
    start_time = time.time()  # 获取当前时间
    while (time.time() - start_time) < timeout_sec:  # 检查是否超时
        for j in range(256 * iterations):
            if (time.time() - start_time) >= timeout_sec:  # 再次检查是否超时
                break
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
    # 时间到后关闭所有 LED
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
    
def check_database_levels():
    while True:
        # 设置时区为伦敦
        today = datetime.datetime.now(pytz.timezone('Europe/London'))
        start_of_day = today.strftime('%Y-%m-%d')
        end_of_day = (today + timedelta(days=1)).strftime('%Y-%m-%d')

        ref = db.reference('/sensorData')
        # 获取当天的数据
        snapshot = ref.order_by_child('timestamp').start_at(start_of_day).end_at(end_of_day).get()
        today_sum = sum(int(entry.get('level', 0)) for entry in snapshot.values() if entry.get('timestamp'))

        print(f"Total level for today ({start_of_day} to {end_of_day}): {today_sum}")
        
        # 访问environment获取今日的liquid_need
        liquid_today = datetime.date.today()
        env_ref = db.reference(f'/environment/{liquid_today}')
        liquid_need_snapshot = env_ref.get()
        if liquid_need_snapshot and 'liquid_need' in liquid_need_snapshot:
            liquid_need = int(liquid_need_snapshot['liquid_need'])
            print(f"Liquid need for today: {liquid_need}")

            # 比较今日总和与需求
            if today_sum > liquid_need:
                rainbowCycle(strip, wait_ms=5, iterations=1, timeout_sec=5)
                time.sleep(2)
                rainbowCycle(strip, wait_ms=5, iterations=1, timeout_sec=5)
                print("GOAL - Today's liquid consumption exceeded the need.")
            else:
                print("Today's liquid consumption has not yet met the need.")
        else:
            print("No liquid need data available for today.")

        # 检查最新30条记录的level是否全为0
        entries = ref.order_by_key().limit_to_last(30).get()
        if all(entry.get('level', 1) == 0 for entry in entries.values()):
            print("All zero in last 30 entries")
            red_breathing_effect()
        else:
            print("Not all zero in last 30 entries")

        time.sleep(1800)  # 等待 30 分钟

def temperature_monitoring():
    current_day = None
    max_temp = None
    liquid_need = 2500

    while True:
        try:
            # 读取温度和湿度
            temperature = dht_device.temperature
            humidity = dht_device.humidity
            print(f"Read temperature: {temperature} C, Humidity: {humidity}%, Liquid Need: {liquid_need}")

            today = datetime.date.today()
            if today != current_day:
                # 新的一天，重置最大温度并创建新的数据库条目
                current_day = today
                max_temp = temperature
                liquid_need = round((0.17 * max_temp - 0.9) * 1000)
                ref = db.reference(f'/environment/{today}')
                ref.set({'max_temperature': temperature, 'humidity': humidity, 'liquid_need': liquid_need})
                print(f"New day detected, resetting max temperature and creating new entry for {today}")
            else:
                # 同一天，更新最大温度
                if temperature > max_temp:
                    max_temp = temperature
                    liquid_need = (0.17 * max_temp - 0.9) * 1000
                    print(liquid_need)
                    ref = db.reference(f'/environment/{today}')
                    ref.update({'max_temperature': temperature, 'humidity': humidity, 'liquid_need': liquid_need})
                    print(f"Updated max temperature to {temperature} C for {today}")

        except RuntimeError as error:
            print(f"Failed to read from DHT20 sensor: {error.args[0]}")

        time.sleep(3600)  # 间隔一小时
        
# 创建并启动线程
thread0 = threading.Thread(target=check_database_levels)
thread0.daemon = True  # 设置为守护线程，这样主程序结束时线程也会结束
thread0.start()

# 创建并启动线程
thread1 = threading.Thread(target=temperature_monitoring)
thread1.daemon = True  # 设置为守护线程，这样主程序结束时线程也会结束
thread1.start()

# 初始化摄像头
picam2 = Picamera2()
preview_config = picam2.create_preview_configuration(main={"size": (640, 480)})

# 加载模型
model = torch.jit.load('/home/MIA/Downloads/CE_dissertation/python_file/DL/model.pt')  # 确保模型路径正确
model.eval()

# 设置图像转换
transform = transforms.Compose([
    transforms.Lambda(lambda image: image.convert('RGB')),  # 确保图像是RGB
    transforms.Resize((128, 128)),  # 根据模型需求调整尺寸
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

camera_active = False  # 标记摄像头是否激活
last_detected_type = "Water"
drink_types = ['Coffee', 'Coke', 'Fanta', 'Juice', 'Water']

try:
    while True:
        current_state = GPIO.input(12)
        print(f"Current GPIO state: {current_state}")

        if current_state == GPIO.HIGH and not camera_active:
            # 启动摄像头
            picam2.configure(preview_config)
            picam2.start()
            camera_active = True
            print("GPIO 16 is HIGH, camera and detection activated...")
            green_breathing_effect()

        elif current_state == GPIO.LOW and camera_active:
            # 停止摄像头
            picam2.stop()
            camera_active = False
            print("GPIO 16 is LOW, camera and detection deactivated...")

        if camera_active:
            # 捕获图像到内存
            image = picam2.capture_array()
            pil_image = Image.fromarray(image)

            # 图像预处理
            input_tensor = transform(pil_image).unsqueeze(0)

            # 模型推理
            with torch.no_grad():
                output = model(input_tensor)
                probabilities = F.softmax(output, dim=1)
                predicted_class = probabilities.argmax(1).item()
                detected_type = drink_types[predicted_class]
                print(f"Predicted drink type: {detected_type}")
                print("Class probabilities:")
                for i, prob in enumerate(probabilities.squeeze().tolist()):
                    print(f"{drink_types[i]}: {prob:.4f}")
                last_detected_type = detected_type
                
        if last_detected_type:
            # Check and update Firebase regardless of GPIO state
            ref = db.reference('/sensorData')
            last_entry = ref.order_by_key().limit_to_last(1).get()
            if last_entry:
                last_key = next(iter(last_entry))
                if 'type' not in last_entry[last_key]:
                    ref.child(last_key).update({'type': last_detected_type})
                    print(f"Updated Firebase at /sensorData with new type: {last_detected_type}")
            
        # 短暂的休眠以避免过高的CPU占用
        time.sleep(5)

finally:
    if camera_active:
        picam2.stop()
    GPIO.cleanup()
    print("Cleaned up resources.")
