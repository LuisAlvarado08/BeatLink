import asyncio
import base64
import requests
import urllib.parse
from bleak import BleakClient, BleakScanner

# === BLE CONFIG ===
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"
ESP_NAME = "ESP32_MusicDisplay"

# === API KEYS ===
TICKETMASTER_API_KEY = "wU4Yw39mOnGqFwI5ydMRGkrSSuYjZGth"
SPOTIFY_CLIENT_ID = "daf22b5ef0f4429389a628b3bf6352fd"
SPOTIFY_CLIENT_SECRET = "aaf89e277fdf4a6f8c8282c7bb65cb8e"

# === Spotify Auth ===
def get_spotify_token():
    """Get a Spotify API access token."""
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(
            f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()
        ).decode()
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("Spotify token retrieved.")
        return token
    else:
        print("Failed to get Spotify token:", response.text)
        return None

spotify_token = get_spotify_token()

# === Get lyrics snippet ===
def get_lyrics_snippet(artist, song):
    """Fetch first few lines of lyrics."""
    try:
        url = f"https://api.lyrics.ovh/v1/{urllib.parse.quote(artist)}/{urllib.parse.quote(song)}"
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            lyrics = res.json().get("lyrics", "")
            snippet = "\n".join(lyrics.splitlines()[:2])
            return snippet.strip() if snippet else "Lyrics not found."
        else:
            return "Lyrics not available."
    except Exception as e:
        print("Lyrics fetch failed:", e)
        return "Lyrics not available."

# === Function: Smart search using Spotify + Ticketmaster + Lyrics ===
def search_music_info(query, spotify_token):
    """Try to detect whether query is artist, song, or lyric snippet."""
    artist_name, song_name, lyrics_snippet, concert_venue, concert_date = (
        "Unknown Artist",
        "Unknown Song",
        "Lyrics unavailable",
        "No Event Found",
        "N/A",
    )

    headers = {"Authorization": f"Bearer {spotify_token}"}
    enc_query = urllib.parse.quote(query)

    try:
        # Search Spotify for both songs and artists
        search_url = f"https://api.spotify.com/v1/search?q={enc_query}&type=track,artist&limit=1"
        res = requests.get(search_url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("tracks", {}).get("items"):
                track = data["tracks"]["items"][0]
                song_name = track["name"]
                artist_name = track["artists"][0]["name"]
            elif data.get("artists", {}).get("items"):
                artist = data["artists"]["items"][0]
                artist_name = artist["name"]
                artist_id = artist["id"]
                # Fetch top song for artist
                t_url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?market=US"
                t_res = requests.get(t_url, headers=headers, timeout=10)
                if t_res.status_code == 200:
                    tracks = t_res.json().get("tracks", [])
                    if tracks:
                        song_name = tracks[0]["name"]
    except Exception as e:
        print("Spotify fetch failed:", e)

    # Lyrics
    lyrics_snippet = get_lyrics_snippet(artist_name, song_name)

    # Ticketmaster concert lookup (only if artist is known)
    if artist_name != "Unknown Artist":
        try:
            tm_url = (
                f"https://app.ticketmaster.com/discovery/v2/events.json?"
                f"keyword={urllib.parse.quote(artist_name)}&classificationName=music&countryCode=US&apikey={TICKETMASTER_API_KEY}"
            )
            r = requests.get(tm_url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                events = data.get("_embedded", {}).get("events", [])
                if events:
                    concert_venue = events[0]["_embedded"]["venues"][0]["name"]
                    concert_date = events[0]["dates"]["start"]["localDate"]
        except Exception as e:
            print("Ticketmaster fetch failed:", e)

    return artist_name, song_name, lyrics_snippet, concert_venue, concert_date


# === Function: Pick ESP32 ===
async def pick_esp32_device():
    print("Scanning for BLE devices (5s)...")
    devices = await BleakScanner.discover(timeout=5.0)
    if not devices:
        print("No BLE devices found. Ensure ESP32 is advertising.")
        return None

    for i, d in enumerate(devices):
        print(f"[{i}] {d.name or '(no name)'}  {d.address}")

    choice = input("\nEnter the number where ESP32_MusicDisplay is located (or press Enter to rescan): ").strip()
    if choice == "":
        return await pick_esp32_device()

    try:
        idx = int(choice)
        return devices[idx]
    except Exception:
        print("Invalid choice.")
        return await pick_esp32_device()


# === Function: Send song info to ESP32 ===
async def send_to_esp32(client, query, spotify_token):
    artist, song, lyrics, concert, date = search_music_info(query, spotify_token)
    message = f"song={song}|artist={artist}|concert={concert}|date={date}"
    print(f"\nSending to ESP32:\n{message}\n")
    try:
        await client.write_gatt_char(CHARACTERISTIC_UUID, message.encode("utf-8"))
        print("Sent successfully!\n")
    except Exception as e:
        print("BLE send failed:", e)

    print("Lyrics Preview:\n----------------")
    print(lyrics)
    print("----------------\n")


# === Main BLE Loop ===
async def connect_and_loop():
    device = await pick_esp32_device()
    if not device:
        return

    print(f"\nConnecting to: {device.name} ({device.address}) ...")
    async with BleakClient(device) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return

        print("Connected! Type an artist, song, or lyric snippet. Type 'exit' to quit.\n")

        while True:
            query = input("Search> ").strip()
            if query.lower() in ("exit", "quit"):
                print("Exiting program.")
                break
            if not query:
                continue

            await send_to_esp32(client, query, spotify_token)


# === Entry point ===
if __name__ == "__main__":
    try:
        asyncio.run(connect_and_loop())
    except KeyboardInterrupt:
        print("\nProgram stopped.")
