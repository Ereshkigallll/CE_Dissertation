# :cup_with_straw: HydroTrack

[![Static Badge](https://img.shields.io/badge/Chinese_Readme-477CB3)](https://github.com/Ereshkigallll/CE_Dissertation/blob/main/README_CN.md)


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