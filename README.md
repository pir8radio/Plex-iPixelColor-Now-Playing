** Yea, AI wrote this readme..  Don't judge, I get lazy when it comes to the readme files. :-)
# 📺 iPixelColor Plex Now‑Playing Display

A Python script that connects your **Plex Media Server** to an **iPixel Color LED sign** over BLE, displaying real‑time “Now Playing” information — or a customizable idle mode with optional built‑in clock display.

This project is designed for reliability and hands‑off operation. Once configured, it runs continuously and automatically reconnects to your LED sign if the bluetooth connection drops.

![ezgif-681aa14bd58a9571](https://github.com/user-attachments/assets/32897c94-65ae-43bb-a333-215d14cc2b11)
* actually much smoother than this, but made this gif and its a little jumpy.


  
<img src="https://github.com/user-attachments/assets/14703d87-58ce-42f8-8c07-02783ef1a506" width="600px"></img>
* idle screen when nothing is playing can be the built in clock, blank, or some text you want like theater or DJ name.
  

---

## ✨ Features

- 🎵 Real‑time Plex “Now Playing” display  
- 🔄 Automatic BLE reconnect with brightness restore  
- 💡 Configurable LED brightness (0–100)  
- 🕒 Optional built‑in clock mode (style 6, 12‑hour, no date)  
- 🧠 First‑run interactive setup (Plex IP, port, token)  
- 🔍 BLE device scanner for iPixel Color LED signs  
- 📝 Auto‑generated and auto‑updated config file  
- ⚙️ Custom idle text or blank screen when nothing is playing

<img width="760" height="409" alt="image" src="https://github.com/user-attachments/assets/45c74a30-9b32-47b1-b276-864345f59e4b" />

  
---

## 📦 Requirements

- Python 3.10+  
- `plexapi` (auto‑installed if missing)  
- `pypixelcolor` (auto‑installed if missing)  
- A BLE‑capable (Bluetooth Low Energy) system  
- An iPixel Color LED sign  

The script installs missing modules automatically.
Works on a Raspberry pi 5B.

---

## 🚀 Installation

Clone the repository:

```
git clone https://github.com/pir8radio/Plex-iPixelColor-Now-Playing
cd Plex-iPixelColor-Now-Playing
```

Run the script:

```
python iPixelColor-Plex.py
```

On first launch, you will be prompted for:

- Plex server IP  
- Plex server port  
- Plex token
- LED Sign Password (if already set on the sign)

Then the script will scan for BLE LED signs and let you select one.

---

## ⚙️ Configuration

You will need to open the config file to enter your particular Plex device, by default it will just monitor any chrome browser playing media. 
You can enable 'print_playing' by setting it to true.  then play some media on your plex device you want to montor, it should then show up in the terminal window.  Enter this title (case sensitive) in the 'target_device' config setting.
All settings are stored in:

```
pixelcolor_config.json
```

Example:

```
{
    "plex_url": "http://127.0.0.1:32400",
    "plex_token": "YOUR_TOKEN_HERE",
    "print_playing": false,
    "target_device": "chrome",
    "poll_interval": 5,
    "use_clock": false,
    "idle_text": " ",
    "text_color": "ff0000",
    "animation_type": 1,
    "animation_speed": 80,
    "ble_address": "AA:BB:CC:DD:EE:FF",
    "brightness": 80,
    "led_sign_password": ""
}
```

### Key Options

| Setting | Description |
|--------|-------------|
| `plex_url` | Your Plex server URL |
| `plex_token` | Plex authentication token |
| `print_playing` | 'true' Helps find correct plex player, will list all devices currently playing something.|
| `target_device` | Which Plex player to monitor |
| `use_clock` | `true` = built‑in LED clock when idle |
| `idle_text` | Text to show when nothing is playing |
| `brightness` | LED brightness (0–100) |
| `animation_type` | Text animation style. See below table. |
| `animation_speed` | Scroll speed |
| `led_sign_password` | Password of sign if set via their app *Not yet supported |



| Animation Type | Effect Name | What It Does |
|--------------|-------------|--------------|
| `0` | Static | Text appears instantly with no movement. |
| `1` | Scroll Left | Standard marquee: text scrolls from right → left. |
| `2` | Scroll Right | Text scrolls from left → right. |
| `3` | Scroll Up | Text moves bottom → top. |
| `4` | Scroll Down | Text moves top → bottom. |
| `5` | Typewriter | Characters appear one at a time. |
| `6` | Blink | Text flashes on/off. |
| `7` | Bounce | Text scrolls left, hits edge, reverses direction. |
| `8` | Slide In | Text slides in from off‑screen and stops. |
| `9` | Slide Out | Text slides out and disappears. |


---

# 🔑 How to Get Your Plex Token

Your Plex token is required for the script to authenticate with your Plex Media Server.  
Here are the easiest ways to retrieve it.

## Method 1 — Quick URL Trick (Fastest)

### 1. Open Plex in Your Browser

Go to:

- https://app.plex.tv  
- **OR** locally: http://127.0.0.1:32400/web/
  

### 2. Find the Token

1. Click the `...` menu on any movie or show.  
2. Select **Get Info**  
3. Scroll down and click **View XML**

<img width="754" height="541" alt="image" src="https://github.com/user-attachments/assets/b3fadcb4-df8f-414e-ad56-5ea603e6fa2c" />


### 3. Copy the Token

The XML opens in a new tab.

Look at the **URL in your browser’s address bar**.

At the very end you’ll see:

```
X-Plex-Token=YOURTOKENHERE
```

Example:

```
https://<server>:32400/library/metadata/123456?<lots-of-text....>&X-Plex-Token=abcd1234efgh5678
```

The part **after** `X-Plex-Token=` is your Plex token.


## ⚠️ Keep Your Token Private

Your Plex token grants full access to your server.  
Do **not** share it publicly or commit it to GitHub.


---

## 🧠 How It Works

1. Connects to Plex and monitors your chosen device  
2. Connects to your iPixel LED sign via BLE  
3. When media starts playing:
   - Sends the title to the LED sign  
4. When playback stops:
   - Shows idle text **or** built‑in clock  
5. If BLE disconnects:
   - Reconnects  
   - Restores brightness  
   - Refreshes display  

---

## 🛠️ Troubleshooting

### LED sign not found

Run:

```
pypixelcolor --scan
```

Ensure Bluetooth is enabled.

### Plex not detected

Verify:
- Plex IP is correct  
- Port is correct  
- Token is valid  
- Device name matches your Plex player  

### Script exits immediately

Run from a terminal to view error output.

---

## 📄 License

You may use, modify, and distribute this software for personal or educational use.
Commercial use of any kind is strictly prohibited without written permission.

---

## ❤️ Credits

Built by Pir8Radio
Powered by [PlexAPI](https://github.com/pushingkarmaorg/python-plexapi) + [PyPixelColor](https://github.com/lucagoc/pypixelcolor)

---

