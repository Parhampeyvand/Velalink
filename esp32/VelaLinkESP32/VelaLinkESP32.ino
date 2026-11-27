/*
  VelaLink ESP32 — Arduino edition

  A lightweight Wi-Fi-to-Wi-Fi router: ESP32 joins an existing Wi-Fi network
  (STA) and creates its own WPA2 access point (AP) for client devices.

  Hardware: ESP32, ESP32-S3, ESP32-C3 or another Arduino-compatible ESP32.
  Requires Arduino-ESP32 3.x / ESP-IDF 5.x with IPv4 NAPT enabled.

  This firmware deliberately does NOT implement VLESS/Xray. An ESP32 does not
  have the resources to safely run an Xray proxy. Use the Linux VelaLink build
  when transparent VLESS routing is required.
*/

#include <WiFi.h>
#include <cstring>
#include <esp_err.h>
#include <esp_netif.h>

// -------- Change these values before uploading --------
constexpr char UPLINK_SSID[] = "YOUR_UPLINK_WIFI";
constexpr char UPLINK_PASSWORD[] = "YOUR_UPLINK_PASSWORD";

constexpr char HOTSPOT_SSID[] = "VelaLink-ESP32";
constexpr char HOTSPOT_PASSWORD[] = "change-this-password"; // 8–63 characters

// The private network offered by the ESP32 access point.
const IPAddress AP_IP(10, 42, 0, 1);
const IPAddress AP_GATEWAY(10, 42, 0, 1);
const IPAddress AP_SUBNET(255, 255, 255, 0);

constexpr uint32_t RECONNECT_DELAY_MS = 10'000;

bool naptEnabled = false;
uint32_t lastReconnectAttempt = 0;

void showStatus() {
  Serial.println();
  Serial.println("--- VelaLink ESP32 status ---");
  Serial.printf("Hotspot: %s\n", HOTSPOT_SSID);
  Serial.printf("Hotspot IP: %s\n", WiFi.softAPIP().toString().c_str());
  Serial.printf("Clients: %u\n", WiFi.softAPgetStationNum());
  Serial.printf("Uplink: %s\n", WiFi.status() == WL_CONNECTED ? "connected" : "disconnected");
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("Uplink IP: %s\n", WiFi.localIP().toString().c_str());
    Serial.printf("Gateway: %s\n", WiFi.gatewayIP().toString().c_str());
  }
  Serial.printf("NAT/NAPT: %s\n", naptEnabled ? "enabled" : "disabled");
  Serial.println("VLESS/Xray: not available on ESP32");
}

bool enableNapt() {
  // ESP-IDF exposes Wi-Fi AP through this standard interface key.
  esp_netif_t *apNetif = esp_netif_get_handle_from_ifkey("WIFI_AP_DEF");
  if (apNetif == nullptr) {
    Serial.println("ERROR: Wi-Fi AP network interface was not found.");
    return false;
  }

  const esp_err_t result = esp_netif_napt_enable(apNetif);
  if (result == ESP_OK || result == ESP_ERR_INVALID_STATE) {
    // INVALID_STATE means it was already enabled.
    Serial.println("NAT/NAPT enabled for hotspot clients.");
    return true;
  }

  Serial.printf("ERROR: could not enable NAT/NAPT: %s\n", esp_err_to_name(result));
  Serial.println("Use Arduino-ESP32 3.x with IPv4 NAPT enabled.");
  return false;
}

void connectUplink() {
  Serial.printf("Connecting to uplink Wi-Fi: %s\n", UPLINK_SSID);
  WiFi.begin(UPLINK_SSID, UPLINK_PASSWORD);
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\nVelaLink ESP32 starting...");

  if (strlen(HOTSPOT_PASSWORD) < 8 || strlen(HOTSPOT_PASSWORD) > 63) {
    Serial.println("ERROR: HOTSPOT_PASSWORD must contain 8–63 characters.");
    while (true) delay(1000);
  }

  WiFi.mode(WIFI_AP_STA);
  WiFi.setSleep(false); // More reliable routing; uses a little more power.

  if (!WiFi.softAPConfig(AP_IP, AP_GATEWAY, AP_SUBNET)) {
    Serial.println("ERROR: could not configure hotspot IP range.");
    while (true) delay(1000);
  }
  if (!WiFi.softAP(HOTSPOT_SSID, HOTSPOT_PASSWORD)) {
    Serial.println("ERROR: could not start the WPA2 hotspot.");
    while (true) delay(1000);
  }

  naptEnabled = enableNapt();
  connectUplink();
  showStatus();
}

void loop() {
  static uint32_t lastStatus = 0;

  if (WiFi.status() != WL_CONNECTED && millis() - lastReconnectAttempt >= RECONNECT_DELAY_MS) {
    lastReconnectAttempt = millis();
    Serial.println("Uplink disconnected; retrying...");
    WiFi.disconnect();
    connectUplink();
  }

  if (millis() - lastStatus >= 30'000) {
    lastStatus = millis();
    showStatus();
  }
}
