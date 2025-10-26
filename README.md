# BeatLink
Bluetooth-powered music display that shows top Spotify songs and upcoming Ticketmaster concerts on an ESP32 LCD.

BeatLink connects your ESP32 microcontroller to the Spotify API and Ticketmaster API, letting users search for an artist, song, or lyric snippet and display the song name, artist, and upcoming concert info directly on an LCD screen via Bluetooth Low Energy (BLE).

------------------------------

## 🚀 Features
- 🔊 Search songs by **artist name**, **song title**, or even **lyrics snippet**  
- 📱 Sends music and concert data wirelessly to an **ESP32 via BLE**
- 🎫 Integrates **Spotify API** for song and artist data  
- 🏟 Integrates **Ticketmaster API** for live concert information  
- 💡 Displays real-time song and concert details on an **LCD display**
- ⚙️ Built using **Python**, **Arduino (C++)**, and **BLE communication**

-------------------------------

## 🧠 Inspiration
We wanted to bridge the gap between music discovery and live events.  
BeatLink helps users instantly connect the songs they love with upcoming concerts nearby — right from a compact BLE-enabled display!

-------------------------------

## 🛠️ Tech Stack
| Component | Description |
|------------|-------------|
| **ESP32** | BLE microcontroller used to receive and display data |
| **Python (Bleak)** | Used to connect to ESP32 via Bluetooth |
| **Spotify Web API** | Fetches song and artist data |
| **Ticketmaster API** | Fetches concert venue and date info |
| **LCD 16x2 Display** | Shows song, artist, and concert details |
| **Arduino IDE** | For flashing ESP32 firmware |

------------------------------

## 🧩 Hardware Setup
- ESP32 development board  
- 16x2 LCD display (I2C or parallel)  
- Potentiometer for brightness 
- Breadboard and jumper wires

**Connection Notes:**
- LCD connected to ESP32 via I2C or digital pins  
- BLE characteristic UUIDs match those defined in Python code  
- Potentiometer pin (optional): adjusts display contrast

------------------------------

## 💻 Software Setup

### 1. Clone the repository
```bash
git clone https://github.com/LuisAlvarado08/BeatLink.git
cd BeatLink
