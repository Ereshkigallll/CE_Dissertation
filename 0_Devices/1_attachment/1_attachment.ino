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

#define PIN_OUT 19

// NTP服务器更新时间
const long utcOffsetInSeconds = 3600; // 例如，对于UTC+1时区
unsigned long lastUploadTime = 0; // 上次上传的时间
const unsigned long uploadInterval = 60000; // 上传间隔，单位毫秒（60000毫秒=1分钟）

int lastLevel = 0; // 上一次记录的液面高度
int totalDecrease = 0; // 一分钟内的总降低值

void setup() {
    pinMode(PIN_OUT, OUTPUT);
    digitalWrite(PIN_OUT, HIGH);
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

    lastUploadTime = millis(); // 初始化上次上报时间
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

void ensureFirebaseConnection() {
    if (!Firebase.ready()) {
        Serial.println("Reconnecting to Firebase");
        firebaseAuth.user.email = FIREBASE_USER_EMAIL;
        firebaseAuth.user.password = FIREBASE_USER_PASSWORD;
        Firebase.reconnectWiFi(true);
        Firebase.begin(&firebaseConfig, &firebaseAuth);

        // 这里只调用 Firebase.ready() 来检查连接状态
        if (Firebase.ready()) {
            Serial.println("Reconnected to Firebase");
        } else {
            Serial.println("Failed to reconnect to Firebase");
        }
    }
}

void loop() {
    timeClient.update();
    ensureFirebaseConnection(); // 每次循环检查并确保连接状态

    if (mySerial.available() >= 4) {
        uint8_t header = mySerial.read();
        if (header == 0xFF) {
            uint8_t highByte = mySerial.read();
            uint8_t lowByte = mySerial.read();
            uint8_t checksum = mySerial.read();
            int currentLevel = (highByte << 8) + lowByte;

            if (lastLevel != 0 && (lastLevel - currentLevel >= 5)) {
                totalDecrease += (lastLevel - currentLevel);
            }
            lastLevel = currentLevel;
        }
    }

    if (millis() - lastUploadTime >= uploadInterval) {
        int vol_liquid = round( 4 * 4 * 3.14 * totalDecrease / 20 );
        FirebaseJson json;
        json.set("timestamp", getFormattedDateTime());
        json.set("device", "ESP32");
        json.set("level", vol_liquid);

        Serial.print("Uploading total significant decrease... ");
        if (Firebase.pushJSON(firebaseData, "/sensorData", json)) {
            Serial.println("Upload successful.");
        } else {
            Serial.println("Failed to upload: " + firebaseData.errorReason());
        }

        totalDecrease = 0; // 重置总降低值
        lastUploadTime = millis(); // 更新上传时间
    }

    delay(100); // 短暂延时以减少CPU占用
}
