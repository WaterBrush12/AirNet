#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// --- CONFIGURATION ---
const char* ssid = "Privat_G2";
const char* password = "G2JUJEMG";
const char* serverUrl = "http://192.168.178.20:8000/air";  // Adjust port if needed

// --- SETUP ---
void setup() {
  Serial.begin(115200);
  delay(1000);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi");
}

// --- LOOP ---
void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    // Prepare JSON payload
    StaticJsonDocument<256> doc;
    doc["uniqueid"] = "esp32_01";

    JsonObject pm = doc.createNestedObject("particulateMatter");
    pm["pm2_5"] = random(0, 100) / 1.0;
    pm["pm10"]  = random(0, 200) / 1.0;

    doc["volatileOrganicCompounds"] = random(0, 500) / 1.0;

    JsonObject gases = doc.createNestedObject("gases");
    gases["CO"]  = random(0, 10) / 10.0;
    gases["NO2"] = random(0, 10) / 100.0;
    gases["O3"]  = random(0, 10) / 100.0;

    String payload;
    serializeJson(doc, payload);

    // Send POST request
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    int httpResponseCode = http.POST(payload);

    if (httpResponseCode > 0) {
      Serial.printf("POST successful, code: %d\n", httpResponseCode);
    } else {
      Serial.printf("POST failed, error: %s\n", http.errorToString(httpResponseCode).c_str());
    }

    http.end();
  } else {
    Serial.println("Wi-Fi disconnected, trying to reconnect...");
    WiFi.reconnect();
  }

  delay(4000);  // wait 4 seconds
}
