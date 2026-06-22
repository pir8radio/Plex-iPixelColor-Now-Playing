# ---------------------------------------------------------
# https://github.com/pir8radio/Plex-iPixelColor-Now-Playing
# ---------------------------------------------------------

import sys
import time
import json
import os
import subprocess
import re
import datetime

# ---------------------------------------------------------
# AUTO-INSTALL ANY MISSING MODULES
# ---------------------------------------------------------
def ensure_module(name):
    try:
        return __import__(name)
    except ImportError:
        print(f'\n⚠️ Missing module "{name}". Installing...\n')
        from subprocess import check_call
        try:
            check_call([sys.executable, "-m", "pip", "install", "--user", name])
            print(f'\n✅ Module "{name}" installed. Restarting...\n')
            sys.exit(1)
        except Exception as e:
            print(f'❌ Failed to install module "{name}": {e}')
            sys.exit(1)

plexapi = ensure_module("plexapi")
pypixelcolor = ensure_module("pypixelcolor")

from plexapi.server import PlexServer
from pypixelcolor.client import Client

# ---------------------------------------------------------
# CONFIGURATION FILE
# ---------------------------------------------------------
CONFIG_FILE = "pixelcolor_config.json"

DEFAULT_CONFIG = {
    "plex_url": "http://127.0.0.1:32400",
    "plex_token": "YOUR_TOKEN_HERE",
    "print_playing": False,
    "target_device": "chrome",
    "poll_interval": 5,
    "use_clock": False,
    "idle_text": " ",
    "text_color": "ff0000",
    "brightness": 80,
    "animation_type": 1,
    "animation_speed": 80,
    "ble_address": None,
    "led_sign_password": ""
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print("\n🆕 First-time setup — let's configure your Plex connection.\n")

        plex_ip = input("🌐 Enter your Plex server IP (default 127.0.0.1): ").strip()
        plex_port = input("🔌 Enter your Plex server port (default 32400): ").strip()
        plex_token = input("🔑 Enter your Plex token: ").strip()
        led_sign_password = input("🔒 (optional) Enter LED sign password (leave blank if none): ").strip()

        if plex_port == "":
            plex_port = "32400"
        if plex_ip == "":
            plex_ip = "127.0.0.1"

        new_cfg = DEFAULT_CONFIG.copy()
        new_cfg["plex_url"] = f"http://{plex_ip}:{plex_port}"
        new_cfg["plex_token"] = plex_token
        new_cfg["led_sign_password"] = led_sign_password

        save_config(new_cfg)

        print("\n✅ Configuration saved. More user options are in the config file created, check them out.\n")
        return new_cfg

    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
    except Exception:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG

    updated = False
    for k, v in DEFAULT_CONFIG.items():
        if k not in data:
            data[k] = v
            updated = True

    if updated:
        save_config(data)

    return data

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=4)

config = load_config()

# ---------------------------------------------------------
# BLE SCANNING
# ---------------------------------------------------------
def run_cli_scan():
    print("\n🔍 Scanning for iPixel Color LED Signs...\n")

    try:
        result = subprocess.run(
            ["pypixelcolor", "--scan"],
            capture_output=True,
            text=True,
            check=True
        )
    except Exception as e:
        print(f"❌ Scanner failed: {e}")
        sys.exit(1)

    output = result.stdout + result.stderr
    print(output)

    devices = re.findall(r"-\s+(.+?)\s+\(([0-9A-F:]{17})\)", output)

    if not devices:
        print("❌ No LED signs found.")
        sys.exit(1)

    print("📡 Devices detected:\n")
    for i, (name, addr) in enumerate(devices):
        print(f"  [{i}] {name} — {addr}")

    print("\n👉 Select a device number:")
    while True:
        choice = input("> ").strip()
        if choice.isdigit() and int(choice) in range(len(devices)):
            name, addr = devices[int(choice)]
            print(f"\n✅ Selected: {name} ({addr})\n")
            config["ble_address"] = addr
            save_config(config)
            return addr

        print("❌ Invalid choice. Try again.")

# ---------------------------------------------------------
# BLE CONNECT + AUTO-RECONNECT
# ---------------------------------------------------------
def connect_ble(address):
    backoff = 1
    while True:
        try:
            client = Client(address=address)
            client.connect()

            print("🔗 BLE connected")
            return client

        except Exception as e:
            print(f"⚠️ BLE connection failed: {e}")
            print(f"⏳ Retrying in {backoff} seconds...")
            subprocess.run(["sudo", "rfkill", "block", "bluetooth"], check=True)
            print("Restarting Bluetooth")
            time.sleep(5)
            subprocess.run(["sudo", "rfkill", "unblock", "bluetooth"], check=True)
            print("Bluetooth re-enabled")
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)

def ensure_ble_connected(client, address):
    try:
        client.get_device_info()
        return client, False
    except Exception:
        print("🔄 BLE connection lost — reconnecting...")
        new_client = connect_ble(address)
        return new_client, True

# ---------------------------------------------------------
# GET BLE ADDRESS (SCAN IF FIRST RUN)
# ---------------------------------------------------------
BLE_ADDRESS = config["ble_address"]

if not BLE_ADDRESS:
    BLE_ADDRESS = run_cli_scan()

print(f"🛜 Using bluetooth device: {BLE_ADDRESS}")

# ---------------------------------------------------------
# INITIALIZE CLIENT + PLEX
# ---------------------------------------------------------
client = connect_ble(BLE_ADDRESS)

client.set_brightness(config["brightness"])
print(f"💡 Brightness set to {config['brightness']}")

plex = PlexServer(config["plex_url"], config["plex_token"])

# ---------------------------------------------------------
# TIME SYNC (ACK IGNORED)
# ---------------------------------------------------------
def sync_time_to_sign(client):
    try:
        client.set_time()
    except Exception:
        pass
    print("⏰ Time sync sent")

# ---------------------------------------------------------
# PLEX DEVICE DETECTION
# ---------------------------------------------------------
def get_now_playing_for_device(target):
    sessions = plex.sessions()

    if config.get("print_playing", True):
        print("\nDevices currently playing on Plex:")
        for s in sessions:
            p = s.players[0] if s.players else None
            if p:
                print(f"  ▶️ {p.title} — {p.product} on {p.platform}")
        print("")

    for session in sessions:
        player = session.players[0] if session.players else None
        if not player:
            continue

        identifiers = {
            player.title,
            player.product,
            player.platform
        }

        identifiers = {str(x).strip() for x in identifiers if x}

        if target in identifiers:

            if session.type == "track":
                return f"{session.grandparentTitle} - {session.title}"

            if session.type == "episode":
                return f"{session.grandparentTitle} S{session.parentIndex}E{session.index}"

            if session.type == "movie":
                return f"{session.title} ({session.year})"

    return None

# ---------------------------------------------------------
# MAIN LOOP
# ---------------------------------------------------------
print(f"⌚ Watching Plex device: {config['target_device']}")

last_title = None
last_clock_sync = 0
CLOCK_SYNC_INTERVAL = 600

while True:
    try:
        client, reconnected = ensure_ble_connected(client, BLE_ADDRESS)

        if reconnected:
            print("🔁 BLE reconnected — refreshing display")
            client.set_brightness(config["brightness"])
            print(f"💡 Brightness restored to {config['brightness']}")
            if config.get("use_clock", False) and last_title == "Idle":
                sync_time_to_sign(client)
                client.set_clock_mode(style=6, show_date=False, format_24=False)
                last_clock_sync = time.time()
            else:
                last_title = None

        now_playing = get_now_playing_for_device(config["target_device"])

        if now_playing:
            if now_playing != last_title:
                print(f"▶️ Now Playing: {now_playing}")
                client.send_text(
                    now_playing,
                    animation=config["animation_type"],
                    speed=config["animation_speed"],
                    color=config["text_color"]
                )
                last_title = now_playing

        else:
            if last_title != "Idle":
                print("⏹️ Nothing playing")

                if config.get("use_clock", False):
                    sync_time_to_sign(client)
                    client.set_clock_mode(style=6, show_date=False, format_24=False)
                    last_clock_sync = time.time()
                else:
                    client.send_text(
                        config["idle_text"],
                        animation=0,
                        color=config["text_color"]
                    )

                last_title = "Idle"

            if config.get("use_clock", False) and last_title == "Idle":
                now_ts = time.time()
                if now_ts - last_clock_sync >= CLOCK_SYNC_INTERVAL:
                    sync_time_to_sign(client)
                    last_clock_sync = now_ts

    except Exception as e:
        print(f"❌ Error: {e}")

    time.sleep(config["poll_interval"])
