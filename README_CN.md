# :cup_with_straw: HydroTrack

[![Static Badge](https://img.shields.io/badge/English_Readme-477CB3)](https://github.com/Ereshkigallll/CE_Dissertation/tree/main)

## 1. Introduction

HydroTrack是一个基于智能物联网追踪用户水分摄入同时通过深度学习模型来分类饮料类型的饮水量追踪系统。整个系统由三个部分组成，安装在杯子底部的Attachment，用于展示饮水量信息、饮料分类以及为Attachment充电的Docking Station以及一个可以手动上传数据的移动应用。通过这三个部分的有机结合，可以帮助用户形成良好的水分摄入的习惯。

## 2. Pre-request

### 2.1 General Request

- 3D打印机以及耗材
- 电烙铁
- 导线
- 激光切割

### 2.2 Attachment
- 820 mA 锂电池
- DFRobot ESP32-C6迷你开发板 [产品wiki](https://wiki.dfrobot.com/SKU_DFR1117_Beetle_ESP32_C6)
- 磁吸充电触点一对
- 电应普非接触式超声波液位传感器

### 2.3 Docking Station
- 树莓派4B
- DHT22
- 微雪 5.65寸 7色电子墨水屏
- DFRobot 红外光声二氧化碳传感器
- 树莓派摄像头
- WS2812 环状LED灯板