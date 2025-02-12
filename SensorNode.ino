#include <WiFi.h>
#include <PubSubClient.h>
#include "aes256.h"
#include <PulseSensorPlayground.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
void SecuritySerialPrinting(String str, int i, uint8_t* buf, int sz) {
  Serial.println(str);
  for (i = 0; i < (sz); ++i) {
    if (buf[i] < 0x10) Serial.print('0');
    Serial.print(char(buf[i]), HEX);
  }
  Serial.println();
}
uint8_t key[] = {
  2, 1, 5, 2, 0, 4, 8, 5,
  2, 1, 5, 2, 0, 4, 8, 5,
  2, 1, 5, 2, 0, 4, 8, 5,
  2, 1, 5, 2, 0, 4, 8, 5
};
aes256_context ctxt;

const char ssid[] = "Duongcuaai",  //"UiTiOt-E3.1";
           password[] = "Dellphaicuamay";   //"UiTiOtAP";
const char mqtt_server[] = "192.168.45.90",
           mqtt_username[] = "nt535o21_nhom1",
           mqtt_password[] = "123456",
           topic[] = "lory265265@gmail.com";
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

const int PULSE_SENSOR_PIN = 0,
          LED_PIN = 13,
          THRESHOLD = 580,
          analogPin = A0;
PulseSensorPlayground pulseSensor;

Adafruit_MPU6050 mpu;
float ax, ay, az, gx, gy, gz,
  magnitude, gyro, z_axis_magnitude;
int state = 0;
void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected!");
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  pulseSensor.analogInput(PULSE_SENSOR_PIN);
  pulseSensor.blinkOnPulse(LED_PIN);
  pulseSensor.setThreshold(THRESHOLD);
  if (pulseSensor.begin())
    Serial.println("Pulse Sensor created successfully!");

  Serial.println("Initializing AES256... ");
  SecuritySerialPrinting("Key: ", 0, key, sizeof(key));
  aes256_init(&ctxt, key);
}
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived on topic: " + String(topic) + ". Message: ");
  String mess = "";
  for (int i = 0; i < length; i++)
    mess += (char)payload[i];
  uint8_t plainData[mess.length()];
  for (int i = 0; i < mess.length(); i++) {
    plainData[i] = (uint8_t)mess[i];
  }
  if (mess.length() > 0 && plainData[mess.length() - 1] == '=')
    plainData[mess.length() - 1] == '0';
  Serial.println(mess);

  SecuritySerialPrinting("Encrypted data: ", 0, plainData, sizeof(plainData));
  unsigned long now = millis();
  aes256_decrypt_ecb(&ctxt, plainData);
  unsigned long time = millis() - now;
  SecuritySerialPrinting("decrypted data: ", 0, plainData, sizeof(plainData));
  Serial.println("Time: " + String(time));
  Serial.println("-----------------------------------------------------------------");
  mess = "";
  for (int i = 0; i < mess.length(); i++) {
    mess += (char)plainData[i];
  }
  Serial.println(mess);
}

void loop() {
  if (!client.connected()) {
    if (client.connect("clientId", mqtt_username, mqtt_password)) {
      client.subscribe(topic);
      Serial.println("Connected to MQTT broker");
    } else {
      Serial.print("Failed to connect to MQTT broker, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
      return;
    }
  }

  int currentBPM = pulseSensor.getBeatsPerMinute() * 0.354978355;
  if (pulseSensor.sawStartOfBeat() && currentBPM > 60) {
    Serial.println(currentBPM);

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    ax = a.acceleration.x;
    ay = a.acceleration.y;
    az = a.acceleration.z;
    gx = g.gyro.x;
    gy = g.gyro.y;
    gz = g.gyro.z;
    magnitude = sqrt(ax * ax + ay * ay + az * az);
    gyro = sqrt(gx * gx + gy * gy + gz * gz);
    z_axis_magnitude = abs(az);

    Serial.print("State: ");
    if (magnitude > 12 && gyro > 0.8) {
      state = 2;  // Chạy
      Serial.println("Chạy");
    } else if (magnitude > 9.8 && gyro > 0.3) {
      state = 1;  // Đi bộ
      Serial.println("Đi bộ");
    } else {
      state = 0;  // Đứng yên
      Serial.println("Đứng yên");
    }

    String str = String(currentBPM) + "/" + String(state);

    uint8_t plainData[str.length()];
    for (int i = 0; i < str.length(); i++) {
      plainData[i] = (uint8_t)str[i];
    }
    Serial.println("Plaintext: " + str);
    SecuritySerialPrinting("Unencrypted data: ", 0, plainData, sizeof(plainData));

    unsigned long now = millis();
    aes256_encrypt_ecb(&ctxt, plainData);
    unsigned long time = millis() - now;

    SecuritySerialPrinting("Encrypted data: ", 0, plainData, sizeof(plainData));

    for (int i = 0; i < sizeof(plainData); i++) {
      Serial.print(plainData[i]);
    }
    Serial.println("");
    Serial.println("Time: " + String(time));
    Serial.println("-----------------------------------------------------------------");

    char data[str.length()];
    for (int i = 0; i < str.length(); i++) {
      data[i] = (char)plainData[i];
      Serial.print(data[i]);
      Serial.print(" ");
    }
    data[str.length()] = '\0';
    Serial.println("");
    Serial.println("-----------------------------------------------------------------");
    client.publish(topic, data);
    delay(5000);
    client.loop();
  }
}