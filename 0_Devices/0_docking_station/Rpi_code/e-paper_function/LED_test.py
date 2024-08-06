from rpi_ws281x import PixelStrip, Color
import time

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

# 主程序
try:
    while True:
        rainbowCycle(strip, wait_ms=20, iterations=1, timeout_sec=5)  # 创建彩虹循环效果
        time.sleep(1)
finally:
    # 清除颜色
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
