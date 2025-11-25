#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// --- CONFIGURATION ---
// WiFi credentials
const char* ssid = "Privat_G2";
const char* password = "G2JUJEMG";
// Backend server details
// IMPORTANT: Use the /air endpoint as it's the correct path for logging data
const char* serverUrl = "http://192.168.178.20:8000/air";
// const char* deviceId = "esp32_01"; // Removed hardcoded device ID
String uniqueDeviceId;

// --- Global state variable to cycle through air quality statuses ---
int state = 0;

// --- SETUP ---
void setup() {
    Serial.begin(115200);
    delay(1000);

    Serial.println("\n");
    Serial.println("-------------------------------------");
    Serial.println("Starting ESP32 Air Quality Sensor");
    Serial.println("-------------------------------------");

    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to Wi-Fi!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    // Use the WiFi MAC address as a unique ID for the device
    uniqueDeviceId = WiFi.macAddress();
    Serial.print("Unique Device ID (MAC Address): ");
    Serial.println(uniqueDeviceId);
}

// --- LOOP ---
void loop() {
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;

        // Prepare JSON payload
        StaticJsonDocument<500> doc;
        doc["uniqueid"] = uniqueDeviceId;

        JsonObject pm = doc.createNestedObject("particulateMatter");
        
        float pm2_5_value;
        // Cycle through different air quality levels
        if (state == 0) {
            // Generate a value in the 'Good' range (1.0 - 11.9)
            pm2_5_value = random(10, 120) / 10.0;
        } else if (state == 1) {
            // Generate a value in the 'Mid' range (12.0 - 35.4)
            pm2_5_value = random(120, 355) / 10.0;
        } else {
            // Generate a value in the 'Bad' range (35.5 - 99.9)
            pm2_5_value = random(355, 1000) / 10.0;
        }
        
        pm["pm2_5"] = pm2_5_value;
        pm["pm10"] = random(0, 200) / 1.0;

        doc["volatileOrganicCompounds"] = random(0, 500) / 1.0;

        JsonObject gases = doc.createNestedObject("gases");
        gases["co"] = random(0, 10) / 10.0;
        gases["no2"] = random(0, 10) / 100.0;
        gases["o3"] = random(0, 10) / 100.0;

        String payload;
        serializeJson(doc, payload);

        // DEBUG: Print the payload to the Serial Monitor
        Serial.println("-------------------------------------");
        Serial.println("Attempting to send data to backend...");
        Serial.print("JSON Payload: ");
        Serial.println(payload);

        // Send POST request
        http.begin(serverUrl);
        http.addHeader("Content-Type", "application/json");
        int httpResponseCode = http.POST(payload);

        Serial.print("HTTP Response Code: ");
        Serial.println(httpResponseCode);
        
        if (httpResponseCode > 0) {
            String response = http.getString();
            Serial.print("Server Response: ");
            Serial.println(response);
        } else {
            Serial.print("HTTP Error: ");
            Serial.println(http.errorToString(httpResponseCode).c_str());
        }

        http.end();
        
        // Increment state and wrap around to 0
        state = (state + 1) % 3;
    } else {
        Serial.println("Wi-Fi disconnected, trying to reconnect...");
        WiFi.reconnect();
    }

    delay(4000); // wait 4 seconds
}