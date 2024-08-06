#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

# 电子墨水屏显示设置
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd5in65f
import time
from PIL import Image, ImageDraw, ImageFont
import traceback
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from datetime import timedelta
import pytz
from rpi_ws281x import PixelStrip, Color
import datetime

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

# Firebase 初始化
cred = credentials.Certificate('/home/MIA/Downloads/CE_dissertation/python_file/e-Paper/RaspberryPi_JetsonNano/python/examples/ce-dissertation-firebase-adminsdk-ouunw-9e48649dc4.json')
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://ce-dissertation-default-rtdb.europe-west1.firebasedatabase.app/'
    })

def get_drink_totals():
    ref = db.reference('/sensorData')
    today = datetime.datetime.now(pytz.timezone('Europe/London'))
    start_of_day = today.strftime('%Y-%m-%d')
    end_of_day = (today + timedelta(days=1)).strftime('%Y-%m-%d')
    
    snapshot = ref.order_by_child('timestamp').start_at(start_of_day).end_at(end_of_day).get()
    drink_types = ['Coke', 'Coffee', 'Water', 'Fanta', 'Juice']
    totals = {drink: 0 for drink in drink_types}
    
    for item in snapshot.values():
        if 'type' in item and 'level' in item:
            if item['type'] in totals:
                totals[item['type']] += item['level']
    
    return totals

# 不要修改现有的 get_total_level() 函数
def get_total_level():
    ref = db.reference('/sensorData')
    today = datetime.datetime.now(pytz.timezone('Europe/London'))
    start_of_today = datetime.datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=pytz.timezone('Europe/London'))
    end_of_today = start_of_today + timedelta(days=1)
    start_of_today_str = start_of_today.strftime('%Y-%m-%d %H:%M:%S')
    end_of_today_str = end_of_today.strftime('%Y-%m-%d %H:%M:%S')
    snapshot = ref.order_by_child('timestamp').start_at(start_of_today_str).end_at(end_of_today_str).get()
    total_level = sum(val['level'] for key, val in snapshot.items() if 'level' in val)
    return round(total_level)

def today_liquid_need():
    liquid_need = 2500
    today = datetime.date.today()
    env_ref = db.reference(f'/environment/{today}')
    liquid_need_snapshot = env_ref.get()
    if liquid_need_snapshot and 'liquid_need' in liquid_need_snapshot:
        liquid_need = int(liquid_need_snapshot['liquid_need'])
        print(f"Liquid need for today: {liquid_need}")
    return liquid_need

logging.basicConfig(level=logging.DEBUG)

previous_level = None  # Initialize previous_level variable

try:
    epd = epd5in65f.EPD()
    logging.info("epd5in65f Demo")
    font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

    while True:
        current_time = datetime.datetime.now(pytz.timezone('Europe/London'))
        if current_time.hour == 0 and current_time.minute < 10:
            # Clear the display once a day at midnight
            epd.init()
            epd.Clear()
            epd.sleep()
            time.sleep(300)

        logging.info("init and Clear")
        epd.init()

        # 获取 Firebase 中的今日总 level
        total_level = get_total_level()     
        liquid_need = today_liquid_need()

        previous_level = total_level  # Update previous_level with current_level
        drink_totals = get_drink_totals()
        coke_total = round(drink_totals['Coke'])
        coffee_total = round(drink_totals['Coffee'])
        water_total = round(drink_totals['Water'])
        fanta_total = round(drink_totals['Fanta'])
        juice_total = round(drink_totals['Juice'])

        intake_percentage = round(total_level * 100 / liquid_need)
        level_display = f'{total_level}mL'  # 格式化为字符串，例如 '300mL'
        per_display = f'{intake_percentage}%'
        coke_display = f'{coke_total}mL'
        coffee_display = f'{coffee_total}mL'
        water_display = f'{water_total}mL'
        fanta_display = f'{fanta_total}mL'
        juice_display = f'{juice_total}mL'

        pixel_up = (500 - 295) * (intake_percentage / 100)
        pixel_loc = round(295 + pixel_up)
        
        # Drawing on the Horizontal image
        logging.info("1.Drawing on the Horizontal image...")
        Himage = Image.open(os.path.join(picdir, 'e-paper_layout.bmp'))
        draw = ImageDraw.Draw(Himage)
        draw.rounded_rectangle((295, 95, 500, 125), radius=5, outline = 0)
        if pixel_loc < 500:
            draw.rounded_rectangle((295, 95, pixel_loc, 125), radius=5, fill=epd.BLUE, outline = 0)
        else:
            draw.rounded_rectangle((295, 95, 500, 125), radius=5, fill=epd.BLUE, outline = 0)
        if pixel_loc >= 350 and pixel_loc < 500:
            per_loc = pixel_loc - 40
            draw.text((per_loc, 100), per_display, font = font18, fill = epd.YELLOW)
        elif pixel_loc >= 500:
            draw.text((450, 100), per_display, font = font18, fill = epd.YELLOW)
        elif pixel_loc < 350:
            per_loc = pixel_loc + 10
            draw.text((per_loc, 100), per_display, font = font18, fill = epd.BLACK)
        draw.text((520, 100), level_display, font=font18, fill=epd.BLACK)
        draw.text((285, 175), water_display, font = font18, fill = epd.BLACK)
        draw.text((285, 223), coke_display, font = font18, fill = epd.BLACK)
        draw.text((285, 271), coffee_display, font = font18, fill = epd.BLACK)
        draw.text((285, 319), fanta_display, font = font18, fill = epd.BLACK)
        draw.text((285, 367), juice_display, font = font18, fill = epd.BLACK)
        if pixel_loc < 500:
            draw.rounded_rectangle((420, 175, 600, 448), radius=1, fill=epd.WHITE)

        epd.display(epd.getbuffer(Himage))
        logging.info("Display updated, going to sleep...")
        epd.sleep()
        
        time.sleep(600)  # 等待10分钟

except IOError as e:
    logging.error(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epd5in65f.epdconfig.module_exit(cleanup=True)
    exit()
