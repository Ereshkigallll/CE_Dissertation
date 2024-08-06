# 监听GPIO并控制LED灯
from gpiozero import Button
from time import sleep
import time
from rpi_ws281x import PixelStrip, Color

# LED 圆环配置
LED_COUNT = 24        # LED 数量
LED_PIN = 18          # GPIO 引脚编号（必须支持 PWM！GPIO 18 是一个好选择）
LED_FREQ_HZ = 800000  # LED 信号频率 (Hz)
LED_DMA = 10          # DMA 通道用于生成信号
LED_BRIGHTNESS = 123  # 设置 LED 最大亮度
LED_INVERT = False    # 当使用 NPN 晶体管电平转换时设置为 True

# 创建 PixelStrip 对象
strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

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

button = Button(12)
while True:
    button.wait_for_press()
    green_breathing_effect()
