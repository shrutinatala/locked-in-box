// parts of this code are taken from
// https://github.com/bitluni/ESP32CameraI2S/
// by bitluni
// released under Public Domain

#include "OV7670.h"
#include <WiFi.h>
#include <WiFiMulti.h>
#include <WiFiClient.h>

// PIN MAPPING: (PINNAME) = (GPIO #)

// synchronization and data sending related constants
const int SIOD = 21; // SCCB SDA
const int SIOC = 22; // SCCB SLC
const int VSYNC = 34;
const int HREF = 35; // SCCB HS
const int XCLK = 32;
const int PCLK = 33;

// pins over which pixel data is sent
const int D0 = 27;
const int D1 = 17;
const int D2 = 16;
const int D3 = 15;
const int D4 = 14;
const int D5 = 13;
const int D6 = 12;
const int D7 = 4;

const OV7670::Mode CAMERA_MODE = OV7670::QQVGA_RGB565;

// wifi settings
#define ssid        "YOUR_WIFI_SSID"
#define password    "YOUR_PASSWORD"

const uint32_t CAPTURE_INTERVAL_MS = 500; // equivalent to 2 FPS 
unsigned long lastCapture = 0;

const char* SERVER_URL = "http://USE.YOUR.SERVER.URL:8000/upload";

OV7670 *camera;
WiFiMulti wifiMulti;

void connectWiFi() {
  // print connection status
  Serial.print("Connecting to WiFi ");
  Serial.print(ssid);

  // configure wifi
  wifiMulti.addAP(ssid, password);
  uint32_t start = millis();

  // keep trying to connect to wifi until timeout
  while (wifiMulti.run() != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
    if (millis() - start > 20000) { // 20s timeout
      Serial.println("\nWiFi connect timeout");
      return;
    }
  }

  // print connection status
  Serial.println("\nWiFi connected; IP: " + WiFi.localIP().toString());
}


void sendFrameToServer(uint8_t* framePtr, size_t frameLen)
{

  // exit if wifi not connected
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi not connected — skipping POST");
    return;
  }

  // connect esp32 to server
  HTTPClient http;
  http.begin(SERVER_URL);

  // setting to configure POSTing raw binary data
  http.addHeader("Content-Type", "application/octet-stream");

  // POST raw bytes
  int httpCode = http.POST(framePtr, frameLen);

  // respond accordingly whether in/valid http code
  if (httpCode > 0) {
    String resp = http.getString();
    Serial.printf("HTTP %d, response len %d\n", httpCode, resp.length());
  } else {
    Serial.printf("HTTP POST failed, error: %d\n", httpCode);
  }

  // close connection
  http.end();
}


void setup() {
  Serial.begin(115200);   // baud rate of 115200 bits per second
  connectWiFi();
  
  camera = new OV7670(CAMERA_MODE, SIOD, SIOC, VSYNC, HREF, XCLK, PCLK, D0, D1, D2, D3, D4, D5, D6, D7);
  Serial.println("Camera initialized with resolution: " + String(camera->xres) + " x " + String(camera->yres));
    
  server.begin();
}

void loop() {

  // ensure camera only captures every CAPTURE_INTERVAL_MS ms
  unsigned long now = millis();
  if (now - lastCapture < CAPTURE_INTERVAL_MS) {
    delay(10);
    return;
  }
  lastCapture = now;

  // capture frame
  Serial.println("Capturing frame...");
  camera->oneFrame();

  // access the frame which the driver stores in I2SCamera::frame and I2SCamera::frameBytes 
  extern unsigned char* frame;
  extern int frameBytes;
  uint8_t* buf = I2SCamera::frame;
  size_t len = (size_t)I2SCamera::frameBytes;

  // detect if no frame captured
  if (!buf || len == 0) {
    Serial.println("No frame captured.");
    return;
  }

  // send frame over http to server
  Serial.printf("Captured %d bytes — sending to server...\n", (int)len);
  sendFrameToServer(buf, len);
}
