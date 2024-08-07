# :cup_with_straw: HydroTrack

[![Static Badge](https://img.shields.io/badge/Chinese_Readme-477CB3)](https://github.com/Ereshkigallll/CE_Dissertation/blob/main/README_CN.md)

![Static Badge](https://img.shields.io/badge/Python-F1F4F1?logo=python&logoColor=%231C84DD)
![Static Badge](https://img.shields.io/badge/C%2B%2B-F1F4F1?logo=cplusplus&logoColor=%231C84DD)
![Static Badge](https://img.shields.io/badge/Flutter-F1F4F1?logo=flutter&logoColor=%2302569B)
![Static Badge](https://img.shields.io/badge/Pytorch-F1F4F1?logo=pytorch&logoColor=%23EE4C2C)
![Static Badge](https://img.shields.io/badge/Raspberry_Pi-F1F4F1?logo=raspberrypi&logoColor=%23A22846)
![Static Badge](https://img.shields.io/badge/Espressif-F1F4F1?logo=espressif&logoColor=%23E7352C)
![Static Badge](https://img.shields.io/badge/Dart-F1F4F1?logo=dart&logoColor=%230175C2)




## 1. Introduction

HydroTrack is an advanced hydration tracking system that utilises smart IoT technology to monitor water intake and employs deep learning models to classify beverage types. The system comprises three components: an Attachment installed at the base of the cup, a Docking Station that displays hydration data, classifies beverages, and charges the Attachment, and a mobile application for manually uploading data. Together, these elements synergistically help users develop healthy hydration habits.

## 2. Pre-request

### 2.1 General Request

- 3D Printer and filament
- Soldering iron
- Laser Cutting

### 2.2 Attachment
- 820 mA lithium polymer battery
- DFRobot ESP32-C6 mini development board [Product wiki](https://wiki.dfrobot.com/SKU_DFR1117_Beetle_ESP32_C6)
- Magnetic Charging Contactor 
- Non-contact ultrasonic liquid level sensor

### 2.3 Docking Station
- Raspberry Pi 4B
- DHT22
- WaveShare 5.65-inches 7 color e-ink screen
- DFRobot infrared CO2 sensor [Product wiki](https://wiki.dfrobot.com/SKU_SEN0536_Gravity_SCD41_Infrared_CO2_Sensor)
- Raspberry Pi camera module
- WS2812 ring LED board