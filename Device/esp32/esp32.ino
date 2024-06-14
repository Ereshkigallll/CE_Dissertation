#include <WiFi.h>
#include <FirebaseESP32.h>
#include "secret.h"
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <HardwareSerial.h>
#include <time.h>

// 初始化WiFiUDP实例
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000);

FirebaseData firebaseData;
HardwareSerial mySerial(1); // 使用第二个硬件串口
FirebaseConfig firebaseConfig;
FirebaseAuth firebaseAuth;

// NTP服务器更新时间
const long utcOffsetInSeconds = 3600; // 例如，对于UTC+1时区

void setup() {
    Serial.begin(115200);
    mySerial.begin(9600, SERIAL_8N1, 17, 16);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(300);
    }
    Serial.println();
    Serial.print("Connected with IP: ");
    Serial.println(WiFi.localIP());

    timeClient.begin();
    timeClient.setTimeOffset(utcOffsetInSeconds);

    configTime(utcOffsetInSeconds, 0, "pool.ntp.org", "time.nist.gov");

    firebaseConfig.host = DATABASE_URL;
    firebaseConfig.api_key = FIREBASE_API_KEY;
    firebaseAuth.user.email = FIREBASE_USER_EMAIL;
    firebaseAuth.user.password = FIREBASE_USER_PASSWORD;

    Firebase.begin(&firebaseConfig, &firebaseAuth);
    Firebase.reconnectWiFi(true);
}

String getFormattedDateTime() {
    struct tm timeinfo;
    if (!getLocalTime(&timeinfo)) {
        Serial.println("Failed to obtain time");
        return "";
    }
    char timeStringBuff[50]; //50 chars should be enough
    strftime(timeStringBuff, sizeof(timeStringBuff), "%Y-%m-%d %H:%M:%S", &timeinfo);
    return String(timeStringBuff);
}

void loop() {
    timeClient.update();

    if (mySerial.available() >= 4) {
        uint8_t header = mySerial.read();
        if (header == 0xFF) {
            uint8_t highByte = mySerial.read();
            uint8_t lowByte = mySerial.read();
            uint8_t checksum = mySerial.read();
            uint16_t level = (highByte << 8) + lowByte;

            FirebaseJson json;
            json.set("timestamp", getFormattedDateTime());
            json.set("device", "ESP32");
            json.set("level", level);

            Serial.print("Pushing JSON data... ");
            if (Firebase.pushJSON(firebaseData, "/sensorData", json)) {
                Serial.println("Data pushed successfully");
            } else {
                Serial.print("Failed to push data: ");
                Serial.println(firebaseData.errorReason());
            }
        }
    }
    delay(100);
}
