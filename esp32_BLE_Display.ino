#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <LiquidCrystal.h>

// === BLE SETUP ===
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"

// === LCD SETUP ===
LiquidCrystal_I2C lcd1(0x27, 16, 2);        // I2C LCD (SDA=21, SCL=22)
LiquidCrystal lcd2(14, 12, 27, 26, 25, 33); // Parallel LCD

BLEServer *pServer = nullptr;
BLECharacteristic *pCharacteristic = nullptr;

// --- Sanitize for I2C LCD ---
void sanitizeAndPrint(LiquidCrystal_I2C &lcd, String text) {
  text.replace("–", "-");
  text.replace("—", "-");
  text.replace("“", "\"");
  text.replace("”", "\"");
  text.replace("‘", "'");
  text.replace("’", "'");
  text.replace("•", "*");
  text.replace("…", "...");
  text.replace("°", " deg");
  for (int i = 0; i < text.length(); i++) if (text[i] < 32 || text[i] > 126) text[i] = ' ';
  if (text.length() > 16) text = text.substring(0, 16);
  lcd.print(text);
}

// --- Sanitize for Parallel LCD ---
void sanitizeAndPrint(LiquidCrystal &lcd, String text) {
  text.replace("–", "-");
  text.replace("—", "-");
  text.replace("“", "\"");
  text.replace("”", "\"");
  text.replace("‘", "'");
  text.replace("’", "'");
  text.replace("•", "*");
  text.replace("…", "...");
  text.replace("°", " deg");
  for (int i = 0; i < text.length(); i++) if (text[i] < 32 || text[i] > 126) text[i] = ' ';
  if (text.length() > 16) text = text.substring(0, 16);
  lcd.print(text);
}

// === Function to parse and display data ===
void displayData(String msg) {
  String song = "", artist = "", concert = "", date = "";

  int songStart = msg.indexOf("song=");
  int artistStart = msg.indexOf("artist=");
  int concertStart = msg.indexOf("concert=");
  int dateStart = msg.indexOf("date=");

  if (songStart != -1) song = msg.substring(songStart + 5, msg.indexOf('|', songStart));
  if (artistStart != -1) artist = msg.substring(artistStart + 7, msg.indexOf('|', artistStart));
  if (concertStart != -1) concert = msg.substring(concertStart + 8, msg.indexOf('|', concertStart));
  if (dateStart != -1) date = msg.substring(dateStart + 5);

  Serial.println("=== BLE Message Received ===");
  Serial.println("Raw: " + msg);
  Serial.println("Song: " + song);
  Serial.println("Artist: " + artist);
  Serial.println("Concert: " + concert);
  Serial.println("Date: " + date);
  Serial.println("============================");

  lcd1.clear();
  lcd1.setCursor(0, 0);
  sanitizeAndPrint(lcd1, song);
  lcd1.setCursor(0, 1);
  sanitizeAndPrint(lcd1, artist);

  lcd2.clear();
  lcd2.setCursor(0, 0);
  sanitizeAndPrint(lcd2, concert);
  lcd2.setCursor(0, 1);
  sanitizeAndPrint(lcd2, date);
}

// === BLE Callback ===
// === BLE Callback ===
class MyCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) override {
    // Handle both possible return types of getValue()
    String msg = "";
    
    // Try getting as Arduino String directly
    #if defined(ARDUINO_ARCH_ESP32)
      msg = pCharacteristic->getValue().c_str();  // works if std::string
    #else
      msg = pCharacteristic->getValue();          // works if String
    #endif

    if (msg.length() == 0) return;
    displayData(msg);
  }
};


// === SETUP ===
void setup() {
  Serial.begin(115200);
  Serial.println("=== ESP32 BLE Music Display ===");

  // LCD init
  Wire.begin(21, 22);
  lcd1.init();
  lcd1.backlight();
  lcd1.print("Waiting BLE...");
  
  lcd2.begin(16, 2);
  lcd2.print("Startup...");

  // BLE init
  BLEDevice::init("ESP32_MusicDisplay");
  pServer = BLEDevice::createServer();
  BLEService *pService = pServer->createService(SERVICE_UUID);

  pCharacteristic = pService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_WRITE | BLECharacteristic::PROPERTY_READ
  );

  pCharacteristic->setCallbacks(new MyCallbacks());
  pCharacteristic->addDescriptor(new BLE2902());

  pService->start();
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->start();

  Serial.println("BLE Ready. Waiting for connection...");
  lcd1.setCursor(0, 1);
  lcd1.print("Ready for BLE!");
}

// === LOOP ===
void loop() {
  delay(1000);
}
