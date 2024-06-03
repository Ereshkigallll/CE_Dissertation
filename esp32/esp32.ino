#include <WiFi.h>
#include <HardwareSerial.h>
#include <secret.h>

const char* ssid = SECRET_SSID;
const char* password = SECRET_PASS;

HardwareSerial mySerial(1); // 使用第二个硬件串口

void setup() {
  Serial.begin(115200);  // 启动串口通信
  mySerial.begin(9600, SERIAL_8N1, 17, 16); // 开始第二串口通信，波特率9600, 8数据位，无奇偶校验位，1停止位，RX引脚17，TX引脚16
  WiFi.begin(ssid, password);  // 开始连接WiFi

  while (WiFi.status() != WL_CONNECTED) {  // 检查WiFi连接状态
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());  // 打印分配到的IP地址
  Serial.println("UART communication started. Waiting for data...");
}

void loop() {
  if (mySerial.available() >= 4) {  // 确保缓冲区至少有4个字节（完整的数据帧）
    uint8_t header = mySerial.read();
    if (header == 0xFF) {  // 确认帧头
      uint8_t highByte = mySerial.read();
      uint8_t lowByte = mySerial.read();
      uint8_t checksum = mySerial.read();  // 读取校验和

      uint16_t level = (highByte << 8) + lowByte;  // 计算液位高度
      Serial.print("Liquid level: ");
      Serial.print(level);
      Serial.println(" mm");

      // 校验和验证（可选）
      uint8_t calculatedChecksum = (header + highByte + lowByte) & 0xFF;
      if (calculatedChecksum == checksum) {
        Serial.println("Checksum OK");
      } else {
        Serial.println("Checksum Error");
      }
    } else {
      Serial.println("Frame header mismatch or corrupted data.");
    }
  }
  delay(100);  // 稍微延迟以等待更多数据
}