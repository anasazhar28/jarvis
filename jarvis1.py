import sys
import traceback

def _fatal(msg):
    try:
        import tkinter as _tk
        from tkinter import messagebox as _mb
        r = _tk.Tk(); r.withdraw()
        _mb.showerror("J.A.R.V.I.S. failed to start", msg)
        r.destroy()
    except Exception:
        print(msg, file=sys.stderr)
    sys.exit(1)

import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, simpledialog
import threading, os, math, time, subprocess, urllib.parse, io, random, sys, json, re, webbrowser, socket, difflib, shutil, ctypes, base64, imaplib, smtplib
from ctypes import wintypes
from datetime import datetime, timedelta
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None
try:
    import requests
    import pandas as pd
    import matplotlib.pyplot as plt
    from PIL import Image, ImageTk
    import ollama
except ImportError as _e:
    _fatal(
        "Missing package: %s\n\n"
        "Open Command Prompt and run:\n"
        "python -m pip install requests pandas matplotlib pillow ollama pypdf numpy sounddevice SpeechRecognition edge-tts pygame-ce\n\n"
        "Also install Ollama from https://ollama.com and run: ollama pull llama3.2"
        % _e
    )

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import numpy as np
    import sounddevice as sd
    import speech_recognition as sr
    VOICE_INPUT = True
except ImportError:
    VOICE_INPUT = False

try:
    import chess
except ImportError:
    chess = None

try:
    import edge_tts
    import pygame
    NATURAL_VOICE = True
except ImportError:
    NATURAL_VOICE = False

JARVIS_MODEL = "llama3.2"
VISION_MODEL = "gemma3:4b"
MESHY_API_KEY = os.environ.get("MESHY_API_KEY", "").strip()
MESHY_BASE_URL = "https://api.meshy.ai/openapi/v2/text-to-3d"
ACCESS_PHRASES = ["daddys home", "i love you 3000", "wake up"]

BG = "#000000"
SIDEBAR = "#010407"
PANEL = "#020508"
PANEL2 = "#05090d"
BLUE = "#00ffff"
GREEN = "#39ff88"
MAGENTA = "#ff3dce"
VIOLET = "#9d7cff"
GOLD = "#ffd166"
TEXT = "#e8f6f8"
MUTED = "#4d6a72"
RED = "#ff5361"
FONT = "Consolas"

SYSTEM_PROMPT = """
You are J.A.R.V.I.S., a personal AI assistant.
Always address the user as Sir.
Never say Sir/Madam, Madam, or Ma'am.
Be intelligent, calm, professional, helpful and slightly witty.
Keep answers natural and reasonably concise.
You are a chatbot only. Do not claim to control the computer.
When LOCATION CONTEXT is provided, use it for weather, local time, and nearby questions.
If location is approximate (IP-based), say so only when precision matters.
"""

WAKE_PATTERN = re.compile(r"\b(?:(?:hey|hay|hi|ok|okay|oi)\s+)?jarvis\b[,.!]?\s*", re.I)
WAKE_PREFIXES = {"hey", "hay", "hi", "ok", "okay", "oi"}
WAKE_NAME_VARIANTS = {"jarvis", "jarevis", "jervis", "jarves", "jarviz", "javis", "jarvice"}
MODE_WAKE_VARIANTS = {
    "jarvis": {"jarvis", "jarevis", "jervis", "jarves", "jarviz", "javis", "jarvice"},
    "vision": {"vision", "vison", "vishon", "vyson"},
    "ultron": {"ultron", "ultronn", "ultrun", "ultrone"},
}

jarvis_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
vision_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
ultron_messages = [{"role": "system", "content": SYSTEM_PROMPT + "\nYou are ULTRON mode: tactical, concise, analytical, and focused on strategy."}]
current_mode = "jarvis"
current_attachment = None
current_attachment_text = None
current_attachment_name = None
chat_titles = []
last_user_text = ""
last_response_text = ""
dashboard_task_label = None
dashboard_reminder_label = None
dashboard_event_label = None
dashboard_memory_label = None
root = None
access_window = None
chat_area = None
input_box = None
status_label = None
history_list = None
jarvis_button = None
vision_button = None
ultron_button = None
weather_value = None
location_value = None
globe_canvas = None
listen_button = None
wake_button = None
attach_button = None
generate_button = None
model3d_button = None
active_3d_close_path = None
active_3d_close_token = None
chess_board = None
chess_active = False
chess_window = None
chess_canvas = None
chess_selected_square = None
chess_status_label = None
chess_animation = None
chess_thinking = False
chess_difficulty = "medium"
chess_ai_battle = False
generated_image_ref = None
thinking_running = False
request_number = 0
active_request_number = 0
globe_angle = 0.0
scan_lat = -80.0
scan_dir = 1.0
w_phase = 0.0
globe_stars = []
clock_label = None
uptime_label = None
channel_label = None
neural_canvas = None
wave_canvas = None
wake_signal_canvas = None
wphase_label = None
session_started = time.time()
location_status = None
access_voice_button = None
access_clap_active = False
vision_panel = None
startup_overlay = None
mic_lock = threading.Lock()
wake_enabled = True
wake_signal_level = 12
wake_signal_state = "SCANNING"
wake_thread_started = False
push_to_talk_active = False
tts_busy = False
tts_stop_event = threading.Event()
tts_process = None
tts_audio_player = None
natural_voice_lock = threading.Lock()
NATURAL_VOICE_NAME = os.environ.get("JARVIS_VOICE") or "en-GB-ThomasNeural"
MODE_VOICE_PROFILES = {
    "jarvis": {
        "system": ["Microsoft George Desktop", "Microsoft George", "Microsoft Hazel Desktop", "Microsoft Hazel", "Microsoft David Desktop", "Microsoft David"],
        "natural": ["en-GB-ThomasNeural", "en-GB-RyanNeural", "en-GB-SoniaNeural", "en-GB-AriaNeural"],
        "rate": "-6%",
        "pitch": "-2Hz",
        "system_rate": -2,
    },
    "vision": {
        "system": ["Microsoft George Desktop", "Microsoft George", "Microsoft David Desktop", "Microsoft David"],
        "natural": ["en-GB-RyanNeural", "en-GB-ThomasNeural", "en-US-AndrewNeural"],
        "rate": "-10%",
        "pitch": "-7Hz",
        "system_rate": -4,
    },
    "ultron": {
        "system": ["Microsoft David Desktop", "Microsoft David", "Microsoft Mark Desktop", "Microsoft Mark", "Microsoft George Desktop", "Microsoft George"],
        "natural": ["en-US-GuyNeural", "en-US-JasonNeural", "en-US-ThomasNeural", "en-US-RogerNeural"],
        "rate": "-18%",
        "pitch": "-22Hz",
        "system_rate": -7,
    },
}
CURRENT_MODE_VOICE_NAME = MODE_VOICE_PROFILES["jarvis"]["system"][0]
NATURAL_VOICE_RATE = os.environ.get("JARVIS_TTS_RATE", MODE_VOICE_PROFILES["jarvis"]["rate"])
NATURAL_VOICE_PITCH = os.environ.get("JARVIS_TTS_PITCH", MODE_VOICE_PROFILES["jarvis"]["pitch"])
NATURAL_VOICE_VOLUME = os.environ.get("JARVIS_TTS_VOLUME", "+0%")
SYSTEM_VOICE_RATE = MODE_VOICE_PROFILES["jarvis"]["system_rate"]
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCATION_PATH = os.path.join(BASE_DIR, "jarvis_location.json")
REMINDERS_PATH = os.path.join(BASE_DIR, "jarvis_reminders.json")
MEMORY_PATH = os.path.join(BASE_DIR, "jarvis_memory.json")
TASKS_PATH = os.path.join(BASE_DIR, "jarvis_tasks.json")
CALENDAR_PATH = os.path.join(BASE_DIR, "jarvis_calendar.json")
EMAIL_FROM = os.environ.get("JARVIS_EMAIL_FROM", "").strip()
EMAIL_PASSWORD = os.environ.get("JARVIS_EMAIL_PASSWORD", "").strip()
SMTP_HOST = os.environ.get("JARVIS_SMTP_HOST", "smtp.gmail.com").strip()
SMTP_PORT = int(os.environ.get("JARVIS_SMTP_PORT", "587").strip() or "587")
SMTP_USE_SSL = os.environ.get("JARVIS_SMTP_SSL", "0").strip() in {"1", "true", "yes"}
IMAP_HOST = os.environ.get("JARVIS_IMAP_HOST", "imap.gmail.com").strip()
reminders = []
memories = []
tasks = []
calendar_events = []
location_info = {
    "city": "Unknown", "region": "", "country": "", "latitude": None, "longitude": None,
    "timezone": "", "ip": "", "source": "none", "weather_text": "Scanning…", "weather_summary": "",
}

TESSERACT_EDGES = []
for _i in range(16):
    for _j in range(_i + 1, 16):
        if bin(_i ^ _j).count("1") == 1:
            a = (
                -1.0 if _i & 1 else 1.0,
                -1.0 if _i & 2 else 1.0,
                -1.0 if _i & 4 else 1.0,
                -1.0 if _i & 8 else 1.0,
            )
            b = (
                -1.0 if _j & 1 else 1.0,
                -1.0 if _j & 2 else 1.0,
                -1.0 if _j & 4 else 1.0,
                -1.0 if _j & 8 else 1.0,
            )
            TESSERACT_EDGES.append((a, b))

NETWORK_CITIES = [
    (40.71, -74.01), (51.51, -0.13), (35.68, 139.69), (25.20, 55.27),
    (-33.87, 151.21), (1.35, 103.82), (55.76, 37.62), (-23.55, -46.63),
    (28.61, 77.21), (34.05, -118.24),
]

WMO_TEXT = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Rime fog", 51: "Light drizzle", 61: "Rain", 63: "Rain",
    65: "Heavy rain", 71: "Snow", 80: "Rain showers", 95: "Thunderstorm",
}


def clamp_byte(value):
    return max(0, min(255, int(value)))


def hex_color(r, g, b):
    return f"#{clamp_byte(r):02x}{clamp_byte(g):02x}{clamp_byte(b):02x}"


def normalize(x, y, z):
    length = math.sqrt(x * x + y * y + z * z) or 1.0
    return x / length, y / length, z / length


def rotate4(x, y, z, w, axw, ayw, azw):
    c, s = math.cos(axw), math.sin(axw)
    x, w = x * c - w * s, x * s + w * c
    c, s = math.cos(ayw), math.sin(ayw)
    y, w = y * c - w * s, y * s + w * c
    c, s = math.cos(azw), math.sin(azw)
    z, w = z * c - w * s, z * s + w * c
    return x, y, z, w


def latlon_to_xyz(lat_deg, lon_deg, angle_deg, radius, tilt_deg=22.0, phase=None):
    if phase is None:
        phase = w_phase
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg + angle_deg)
    x = math.cos(lat) * math.sin(lon)
    y = math.sin(lat)
    z = math.cos(lat) * math.cos(lon)
    tilt = math.radians(tilt_deg)
    y, z = y * math.cos(tilt) - z * math.sin(tilt), y * math.sin(tilt) + z * math.cos(tilt)
    x, y, z, w = rotate4(x, y, z, 0.0, phase, phase * 0.73, phase * 0.31)
    k = 1.18 / max(0.35, 1.22 + w)
    return x * k * radius, y * k * radius, z * k * radius


def project_xyz(x, y, z, cx, cy, radius):
    cam = radius * 4.6
    scale = cam / max(0.2, cam - z)
    return cx + x * scale, cy - y * scale, z, scale


def project_latlon(lat_deg, lon_deg, angle_deg, radius, cx, cy, phase=None):
    x, y, z = latlon_to_xyz(lat_deg, lon_deg, angle_deg, radius, phase=phase)
    px, py, pz, scale = project_xyz(x, y, z, cx, cy, radius)
    return px, py, pz, scale, x, y, z


def rotate_y(x, y, z, angle_deg):
    a = math.radians(angle_deg)
    ca, sa = math.cos(a), math.sin(a)
    return x * ca + z * sa, y, -x * sa + z * ca


def project_tesseract_vertex(vx, vy, vz, vw, radius, cx, cy):
    x, y, z, w = rotate4(vx, vy, vz, vw, w_phase * 1.4, w_phase * 0.9, globe_angle * 0.02)
    dist = 3.0
    k = dist / max(0.35, dist - w)
    return project_xyz(x * k * radius * 0.72, y * k * radius * 0.72, z * k * radius * 0.72, cx, cy, radius)


def face_fill(nx, ny, nz, radius, lat, scan):
    view_z = nz / radius
    ndl = max(0.0, nx * -0.42 + ny * 0.48 + nz * 0.76) / radius
    fresnel = max(0.0, 1.0 - max(0.0, view_z)) ** 1.55
    band = max(0.0, 1.0 - abs(lat - scan) / 9.0)
    r = 70 + 125 * ndl + 120 * fresnel + 55 * band
    g = 28 + 88 * ndl + 92 * fresnel + 52 * band
    b = 2 + 8 * ndl + 5 * fresnel + 2 * band
    r += 35 * band
    return hex_color(r, g, b)


def hud_button(parent, text, command, fg=BLUE, bg="#031016", **kwargs):
    return tk.Button(
        parent, text=text, command=command, font=(FONT, 9, "bold"), bg=bg, fg=fg,
        activebackground="#00c8d8", activeforeground="#000000", relief=tk.FLAT, bd=0,
        highlightthickness=1, highlightbackground=fg, highlightcolor=fg, cursor="hand2", **kwargs,
    )


def framed(parent, bg=None):
    return tk.Frame(parent, bg=bg or PANEL, highlightbackground="#00a8b8", highlightthickness=1)


def draw_polyline(points, color, width, smooth=True):
    if len(points) >= 4:
        globe_canvas.create_line(*points, fill=color, width=width, smooth=smooth, tags="globe")


def draw_orbit_ring(cx, cy, radius, tilt_deg, yaw_deg, color, width=1, lift=1.22):
    pts_front, pts_back = [], []
    n = 72
    for i in range(n + 1):
        a = (2 * math.pi * i) / n
        x = radius * lift * math.cos(a)
        y = radius * lift * math.sin(a) * math.cos(math.radians(tilt_deg))
        z = radius * lift * math.sin(a) * math.sin(math.radians(tilt_deg))
        x, y, z = rotate_y(x, y, z, yaw_deg)
        px, py, pz, _ = project_xyz(x, y, z, cx, cy, radius)
        if pz >= 0:
            if len(pts_back) >= 4:
                draw_polyline(pts_back, "#06323f", 1, True)
                pts_back = []
            pts_front += [px, py]
        else:
            if len(pts_front) >= 4:
                draw_polyline(pts_front, color, width, True)
                pts_front = []
            pts_back += [px, py]
    if len(pts_back) >= 4:
        draw_polyline(pts_back, "#06323f", 1, True)
    if len(pts_front) >= 4:
        draw_polyline(pts_front, color, width, True)


def draw_great_arc(lat1, lon1, lat2, lon2, angle, radius, cx, cy):
    ax, ay, az = latlon_to_xyz(lat1, lon1, angle, 1.0)
    bx, by, bz = latlon_to_xyz(lat2, lon2, angle, 1.0)
    dot = max(-1.0, min(1.0, ax * bx + ay * by + az * bz))
    if abs(dot) > 0.97:
        return
    points = []
    n = 22
    for i in range(n + 1):
        t = i / n
        mx, my, mz = normalize(ax * (1 - t) + bx * t, ay * (1 - t) + by * t, az * (1 - t) + bz * t)
        lift = 1.0 + 0.22 * math.sin(t * math.pi)
        px, py, pz, _ = project_xyz(mx * radius * lift, my * radius * lift, mz * radius * lift, cx, cy, radius)
        if pz >= -radius * 0.05:
            points += [px, py]
        elif len(points) >= 4:
            draw_polyline(points, MAGENTA, 1, True)
            points = []
    if len(points) >= 4:
        draw_polyline(points, MAGENTA, 1, True)


def ensure_starfield():
    global globe_stars
    if len(globe_stars) < 90:
        random.seed(7)
        globe_stars = [(random.random(), random.random(), 0.35 + random.random() * 0.65) for _ in range(110)]


def normalize_access_phrase(text):
    t = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower().replace("'", ""))
    t = " ".join(t.split())
    t = re.sub(r"\bclap\s+clap\b", " ", t)
    t = t.replace("daddy is home", "daddys home").replace("daddies home", "daddys home")
    t = t.replace("three thousand", "3000").replace("3 000", "3000")
    return t


def phrase_unlocks(text):
    heard = normalize_access_phrase(text)
    if not heard:
        return False
    for phrase in ACCESS_PHRASES:
        key = normalize_access_phrase(phrase)
        if heard == key or key in heard:
            return True
    return False


def grant_access():
    global access_clap_active
    access_clap_active = False
    access_status.config(text="✓ ACCESS GRANTED", fg=GREEN)
    try:
        access_entry.delete(0, tk.END)
    except Exception:
        pass
    access_window.after(450, open_jarvis)


def check_access(event=None):
    if phrase_unlocks(access_entry.get()):
        grant_access()
    else:
        access_status.config(text="✗ ACCESS DENIED", fg=RED)
        access_entry.delete(0, tk.END)


def listen_access_phrase():
    if not VOICE_INPUT:
        access_status.config(text="VOICE LOCK OFF  ·  pip install sounddevice numpy SpeechRecognition", fg=RED)
        return
    if access_voice_button:
        access_voice_button.config(state=tk.DISABLED, text="LISTENING…")
    access_status.config(text="SPEAK ACCESS PHRASE  ·  6s", fg=GOLD)
    threading.Thread(target=listen_access_worker, daemon=True).start()


def start_access_clap_listener():
    global access_clap_active
    if not VOICE_INPUT or access_clap_active:
        return
    access_clap_active = True
    threading.Thread(target=access_clap_listener, daemon=True).start()


def access_clap_listener():
    global access_clap_active
    while access_clap_active:
        try:
            if clap_detected(record_pcm(1.4)):
                access_clap_active = False
                access_window.after(0, grant_access)
                return
        except Exception:
            # Remain quiet while the access gate is idle; the button still exposes microphone errors.
            time.sleep(0.4)


def listen_access_worker():
    def restore():
        if access_voice_button:
            access_voice_button.config(state=tk.NORMAL, text="SPEAK PHRASE")
    try:
        heard = transcribe_pcm(record_until_silence(min_duration=1.2, silence_window=1.0, max_duration=9.0))

        def apply():
            access_entry.delete(0, tk.END)
            access_entry.insert(0, heard)
            if phrase_unlocks(heard):
                grant_access()
            else:
                access_status.config(text=f"✗ VOICE DENIED  ·  heard: {heard}", fg=RED)
                restore()
        access_window.after(0, apply)
    except sr.UnknownValueError:
        access_window.after(0, lambda: access_status.config(text="✗ NO SPEECH DETECTED  ·  TRY AGAIN", fg=RED))
        access_window.after(0, restore)
    except Exception as e:
        access_window.after(0, lambda: access_status.config(text=f"✗ MIC ERROR  ·  {e}", fg=RED))
        access_window.after(0, restore)


def open_jarvis():
    global access_window
    access_window.destroy()
    create_jarvis_window()


def display_user(text):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"\nYOU  ·  {time.strftime('%H:%M:%S')}\n", "user_label")
    chat_area.insert(tk.END, text + "\n", "user_text")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)


def display_response(text, label=None):
    global last_response_text
    label = label or {"jarvis": "JARVIS", "vision": "VISION", "ultron": "ULTRON"}.get(current_mode, "JARVIS")
    last_response_text = str(text or "")
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"\n{label}  ·  {time.strftime('%H:%M:%S')}  ·  SECURE\n", "jarvis_label")
    chat_area.insert(tk.END, text + "\n", "jarvis_text")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)
    if status_label is not None:
        status_label.config(text=f"{label}  //  ONLINE  •  RESPONSE READY", fg=GREEN)
        root.after(1400, refresh_ready_status)
    if current_mode in {"jarvis", "ultron"}:
        refresh_ready_status()
    else:
        status_label.config(text=f"{label}  //  ONLINE  •  READY")


def display_error(error):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, "\nSYSTEM ERROR\n", "error_label")
    chat_area.insert(tk.END, str(error) + "\n", "error_text")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)
    status_label.config(text="SYSTEM: ERROR", fg=RED)


def start_thinking():
    global thinking_running
    thinking_running = True
    animate_thinking(0)


def animate_thinking(n):
    if not thinking_running or root is None:
        return
    frames = [
        "NEURAL CORE  //  COMPUTING ·",
        "NEURAL CORE  //  COMPUTING ··",
        "NEURAL CORE  //  COMPUTING ···",
        "NEURAL CORE  //  COMPUTING ····",
    ]
    try:
        status_label.config(text=frames[n % 4], fg=BLUE)
        root.after(180, lambda: animate_thinking(n + 1))
    except Exception:
        pass


def stop_thinking():
    global thinking_running
    thinking_running = False


def stop_speaking():
    """Immediately stop JARVIS voice output and cancel the current TTS process."""
    global tts_busy, tts_process, tts_audio_player
    tts_stop_event.set()
    proc = tts_process
    if proc is not None:
        try:
            proc.terminate()
        except Exception:
            pass
        try:
            proc.kill()
        except Exception:
            pass
    tts_process = None
    if tts_audio_player:
        try:
            tts_audio_player.stop()
        except Exception:
            pass
    tts_busy = False


def is_stop_command(text):
    t = re.sub(r"[^a-z0-9\s]", " ", (text or "").lower())
    t = " ".join(t.split())
    if not t or re.search(r"\b(?:do not|dont|never)\s+stop\b", t):
        return False
    return bool(re.search(r"\b(?:stop|quiet|cancel|enough|shut up|never mind)\b", t))


def is_image_request(text):
    t = " ".join((text or "").lower().split())
    media = r"(?:image|picture|photo|artwork|illustration|wallpaper|drawing|rendering)"
    verbs = r"(?:generate|create|make|draw|render|produce|show)"
    return bool(
        re.search(rf"\b{verbs}\b.*\b{media}\b", t)
        or re.search(rf"\b{media}\b.*\b(?:of|about|show|{verbs})\b", t)
        or re.search(r"\b(?:draw|render)\b\s+(?:me\s+)?(?:a|an|the)?\s*\w+", t)
    )


def is_3d_request(text):
    t = " ".join((text or "").lower().split())
    return bool(
        re.search(r"\b(?:make|create|generate|build|design|model|render)\b.*\b(?:3d|three dimensional|3-dimensional)\b", t)
        or re.search(r"\b(?:3d|three dimensional|3-dimensional)\b.*\b(?:model|suit|armor|armour|object)\b", t)
    )


def is_simple_shape_request(text):
    normalized = " ".join((text or "").lower().split())
    return bool(re.search(r"\b(?:circle|disc|disk|square|rectangle|triangle|cube|sphere|cylinder|cone|torus|pyramid|capsule|octahedron|icosahedron|dodecahedron|tetrahedron|knot)\b", normalized))


def is_shape_collection_request(text):
    normalized = " ".join((text or "").lower().split())
    return bool(
        re.search(r"\b(?:create|make|generate|build|design|render|model)\b.*\b(?:shapes?|geometric shapes?)\b", normalized)
        or re.search(r"\b(?:shapes?|geometric shapes?)\b.*\b(?:3d|three dimensional|three-dimensional)\b", normalized)
        or re.search(r"\b(?:3d|three dimensional|three-dimensional)\b.*\b(?:shapes?|geometric shapes?)\b", normalized)
        or re.search(r"\b(?:model|scene|render)\s+(?:of|with|for)\s+(?:shapes?|geometric shapes?)\b", normalized)
    )


def is_close_3d_request(text):
    normalized = " ".join((text or "").lower().split())
    return bool(re.search(r"\b(?:close|exit|hide)\b.*\b(?:3d|three dimensional|model|viewer|page)\b", normalized))


def close_3d_model_page():
    """Ask the active browser viewer to leave the model page."""
    if not active_3d_close_path:
        display_response("There is no active 3D model page to close, Sir.")
        return
    try:
        with open(active_3d_close_path, "w", encoding="utf-8") as close_file:
            close_file.write("CLOSE")
        display_response("Closing the active 3D model page, Sir.")
    except OSError as error:
        display_error(f"Could not close the 3D model page: {error}")


def is_jarvis_shutdown_command(text):
    normalized = " ".join((text or "").lower().split())
    return bool(re.search(r"\b(?:shut down|shutdown|close|exit|quit|stop)\s+(?:the\s+)?jarvis\b", normalized))


def shutdown_jarvis():
    stop_speaking()
    stop_thinking()
    if root is not None:
        display_response("J.A.R.V.I.S. shutting down. Goodbye, Sir.")
        root.after(350, root.destroy)


def is_wake_command(text, enabled):
    t = " ".join((text or "").lower().split())
    if enabled:
        return bool(re.search(r"\b(?:wake|listening|listen)\b.*\b(?:off|disable|stop)\b", t))
    return bool(re.search(r"\b(?:wake|listening|listen)\b.*\b(?:on|enable|start)\b", t))


def _pc_target_path(target):
    aliases = {
        "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
        "music": os.path.join(os.path.expanduser("~"), "Music"),
        "videos": os.path.join(os.path.expanduser("~"), "Videos"),
    }
    cleaned = target.strip().strip('"\'').rstrip(".,!? ")
    path = aliases.get(cleaned.lower(), cleaned)
    if not os.path.isabs(path):
        path = os.path.join(os.path.expanduser("~"), path)
    return os.path.abspath(path)


def load_reminders():
    global reminders
    try:
        with open(REMINDERS_PATH, "r", encoding="utf-8") as f:
            reminders = json.load(f)
        if not isinstance(reminders, list):
            reminders = []
    except (OSError, json.JSONDecodeError):
        reminders = []


def save_reminders():
    try:
        with open(REMINDERS_PATH, "w", encoding="utf-8") as f:
            json.dump(reminders, f, indent=2)
    except OSError:
        pass


def format_reminder_time(timestamp):
    return datetime.fromtimestamp(timestamp).strftime("%a %d %b at %I:%M %p")


def add_reminder(timestamp, message, kind="reminder"):
    reminders.append({"time": timestamp, "message": message, "kind": kind})
    reminders.sort(key=lambda item: item["time"])
    save_reminders()
    label = "Alarm" if kind == "alarm" else "Reminder"
    response = f"{label} set for {format_reminder_time(timestamp)}: {message}, Sir."
    display_response(response)
    speak_text(response)


def check_reminders():
    now = time.time()
    due = [item for item in reminders if item.get("time", 0) <= now]
    if due:
        for item in due:
            message = f"{item.get('kind', 'Reminder').title()}: {item.get('message', 'scheduled event')}, Sir."
            display_response(message)
            speak_text(message)
        reminders[:] = [item for item in reminders if item not in due]
        save_reminders()
    if root:
        root.after(1000, check_reminders)


def handle_reminder_command(normalized):
    if re.search(r"\b(?:show|list|what are)\b.*\b(?:reminders?|alarms?)\b", normalized):
        upcoming = [item for item in reminders if item.get("time", 0) > time.time()]
        if not upcoming:
            display_response("You have no upcoming reminders or alarms, Sir.")
        else:
            lines = [
                f"{index}. {item.get('kind', 'Reminder').title()}  ·  {format_reminder_time(item['time'])}  ·  {item['message']}"
                for index, item in enumerate(upcoming, 1)
            ]
            display_response("Upcoming schedule, Sir:\n" + "\n".join(lines))
        return True

    if re.search(r"\b(?:cancel|clear|delete)\s+(?:all\s+)?(?:my\s+)?(?:reminders?|alarms?)\b", normalized):
        reminders.clear()
        save_reminders()
        display_response("All reminders and alarms have been cancelled, Sir.")
        speak_text("All reminders and alarms have been cancelled, Sir.")
        return True

    relative = re.search(
        r"\b(?:remind me|set a reminder)\s+(?:in)\s+(\d+)\s*(seconds?|minutes?|hours?|days?)\s+(?:to|that)\s+(.+)$",
        normalized,
    )
    if relative:
        amount = int(relative.group(1))
        unit = relative.group(2).lower()
        seconds = amount * {"second": 1, "seconds": 1, "minute": 60, "minutes": 60,
                            "hour": 3600, "hours": 3600, "day": 86400, "days": 86400}[unit]
        add_reminder(time.time() + seconds, relative.group(3).rstrip("."))
        return True

    at_time = re.search(
        r"\b(?:remind me|set (?:an? )?alarm|set a reminder)\s+(?:at|for)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?(?:\s+(?:to|that)\s+(.+))?$",
        normalized,
    )
    if at_time:
        hour = int(at_time.group(1))
        minute = int(at_time.group(2) or 0)
        meridiem = at_time.group(3)
        if meridiem:
            if hour < 1 or hour > 12:
                display_error("Please use an hour from 1 to 12 with AM or PM, Sir.")
                return True
            if meridiem == "pm" and hour != 12:
                hour += 12
            if meridiem == "am" and hour == 12:
                hour = 0
        elif hour > 23:
            display_error("Please use a valid 24-hour time, Sir.")
            return True
        scheduled = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
        if scheduled <= datetime.now():
            scheduled += timedelta(days=1)
        message = (at_time.group(4) or "your scheduled event").rstrip(".")
        kind = "alarm" if "alarm" in normalized else "reminder"
        add_reminder(scheduled.timestamp(), message, kind)
        return True
    return False


def load_memories():
    global memories
    try:
        with open(MEMORY_PATH, "r", encoding="utf-8") as f:
            memories = json.load(f)
        if not isinstance(memories, list):
            memories = []
    except (OSError, json.JSONDecodeError):
        memories = []


def save_memories():
    try:
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(memories, f, indent=2, ensure_ascii=True)
    except OSError:
        pass


def memory_context():
    if not memories:
        return ""
    return "\n\nPERSISTENT USER MEMORY:\n" + "\n".join(f"- {item}" for item in memories[-50:])


def load_tasks():
    global tasks
    try:
        with open(TASKS_PATH, "r", encoding="utf-8") as f:
            tasks = json.load(f)
        if not isinstance(tasks, list):
            tasks = []
    except (OSError, json.JSONDecodeError):
        tasks = []


def save_tasks():
    try:
        with open(TASKS_PATH, "w", encoding="utf-8") as f:
            json.dump(tasks, f, indent=2)
    except OSError:
        pass


def load_calendar():
    global calendar_events
    try:
        with open(CALENDAR_PATH, "r", encoding="utf-8") as f:
            calendar_events = json.load(f)
        if not isinstance(calendar_events, list):
            calendar_events = []
    except (OSError, json.JSONDecodeError):
        calendar_events = []


def save_calendar():
    try:
        with open(CALENDAR_PATH, "w", encoding="utf-8") as f:
            json.dump(calendar_events, f, indent=2)
    except OSError:
        pass


def parse_event_datetime(text):
    now = datetime.now()
    lower = (text or "").lower()
    base_day = now
    weekday_map = {
        "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4,
        "saturday": 5, "sunday": 6,
    }
    if "tomorrow" in lower:
        base_day = now + timedelta(days=1)
    elif any(day in lower for day in weekday_map):
        for day_name, index in weekday_map.items():
            if day_name in lower:
                days_ahead = (index - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                base_day = now + timedelta(days=days_ahead)
                break
    time_match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text, re.I)
    hour = 9
    minute = 0
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridiem = (time_match.group(3) or "").lower()
        if meridiem == "pm" and hour < 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
        if hour > 23 or minute > 59:
            raise ValueError("Please use a valid time for the event, Sir.")
    start = base_day.replace(hour=hour, minute=minute, second=0, microsecond=0)
    duration_match = re.search(r"for\s+(\d+)\s*(minute|minutes|hour|hours)", text, re.I)
    duration = 60
    if duration_match:
        value = int(duration_match.group(1))
        unit = duration_match.group(2).lower()
        duration = value * (60 if unit.startswith("minute") else 3600)
    return start, duration


def add_calendar_event(title, when_text):
    start, duration = parse_event_datetime(when_text)
    end = start + timedelta(minutes=duration // 60 if duration % 60 == 0 else int(duration / 60))
    event = {"title": title, "start": start.isoformat(), "end": end.isoformat(), "duration_minutes": int(duration / 60)}
    calendar_events.append(event)
    calendar_events.sort(key=lambda item: item["start"])
    save_calendar()
    refresh_dashboard()
    display_response(f"Event added, Sir: {title} at {start.strftime('%a %d %b %Y %I:%M %p')}.")
    return True


def list_calendar_events(limit=10):
    if not calendar_events:
        return "You do not have any scheduled events, Sir."
    upcoming = sorted(calendar_events, key=lambda item: item["start"])[:limit]
    lines = []
    for index, event in enumerate(upcoming, 1):
        start = datetime.fromisoformat(event["start"])
        end = datetime.fromisoformat(event["end"])
        lines.append(f"{index}. {event['title']}  ·  {start.strftime('%a %d %b %Y %I:%M %p')} to {end.strftime('%I:%M %p')}")
    return "Upcoming events, Sir:\n" + "\n".join(lines)


def handle_calendar_command(normalized):
    if re.search(r"\b(?:show|list|what are)\b.*\b(?:my\s+)?(?:calendar|events?)\b", normalized):
        display_response(list_calendar_events())
        return True

    if re.search(r"\b(?:clear|delete|remove all)\s+(?:my\s+)?(?:calendar|events?)\b", normalized):
        calendar_events.clear()
        save_calendar()
        refresh_dashboard()
        display_response("All scheduled events have been cleared, Sir.")
        return True

    delete_match = re.search(r"\b(?:delete|remove)\s+(?:event\s+)?(\d+)\b", normalized)
    if delete_match:
        index = int(delete_match.group(1)) - 1
        if 0 <= index < len(calendar_events):
            item = calendar_events.pop(index)
            save_calendar()
            refresh_dashboard()
            display_response(f"Deleted event {index + 1}, Sir: {item['title']}")
            return True
        display_response("That event number does not exist, Sir.")
        return True

    add_match = re.search(r"\b(?:add|new|schedule|create)\s+(?:an?\s+)?(?:event|meeting|appointment)\s+(.+)$", normalized)
    if add_match:
        event_text = add_match.group(1).strip().rstrip(".")
        if not event_text:
            display_response("Please tell me the event title and time, Sir.")
            return True
        title_match = re.match(r"(.+?)\s+(?:on|at|for)\s+.+$", event_text, re.I)
        title = title_match.group(1).strip() if title_match else event_text
        when_text = event_text
        if title_match:
            when_text = event_text[len(title_match.group(1)).strip():].strip()
        try:
            add_calendar_event(title, when_text)
            return True
        except ValueError as error:
            display_error(str(error))
            return True

    if re.search(r"\b(?:event|calendar)\b", normalized):
        display_response("Say add event followed by the title and time, or ask me to list events, Sir.")
        return True
    return False


def email_configuration_ready():
    return bool(EMAIL_FROM and EMAIL_PASSWORD)


def send_email(recipient, subject, body):
    if not email_configuration_ready():
        raise RuntimeError("Email is not configured. Set JARVIS_EMAIL_FROM and JARVIS_EMAIL_PASSWORD first, Sir.")
    msg = "\r\n".join([
        f"From: {EMAIL_FROM}",
        f"To: {recipient}",
        f"Subject: {subject}",
        "",
        body,
    ])
    if SMTP_USE_SSL:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, recipient, msg)
    else:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.sendmail(EMAIL_FROM, recipient, msg)
    return True


def check_inbox(limit=5):
    if not (EMAIL_FROM and EMAIL_PASSWORD):
        raise RuntimeError("Email is not configured. Set JARVIS_EMAIL_FROM and JARVIS_EMAIL_PASSWORD first, Sir.")
    with imaplib.IMAP4_SSL(IMAP_HOST) as mail:
        mail.login(EMAIL_FROM, EMAIL_PASSWORD)
        mail.select("INBOX")
        _, message_data = mail.search(None, "ALL")
        ids = message_data[0].decode("utf-8", "ignore").split()
        recent = list(reversed(ids[-limit:])) if ids else []
        if not recent:
            return "Your inbox is empty, Sir."
        lines = []
        for msg_id in recent:
            _, payload = mail.fetch(msg_id, "(RFC822)")
            raw = payload[0][1]
            try:
                from email import message_from_bytes
                msg = message_from_bytes(raw)
                lines.append(f"- {msg.get('From', 'Unknown')}  ·  {msg.get('Subject', 'No subject')}")
            except Exception:
                lines.append(f"- Message {msg_id}")
        return "Recent inbox messages, Sir:\n" + "\n".join(lines)


def handle_email_command(normalized):
    if re.search(r"\b(?:check|read|show)\s+(?:my\s+)?(?:mail|email|inbox)\b", normalized):
        try:
            display_response(check_inbox())
        except Exception as error:
            display_error(str(error))
        return True

    send_match = re.search(r"\b(?:send|email)\s+(?:to\s+)?(.+?)(?:\s+with\s+subject\s+|\s+subject\s+)(.+?)(?:\s+message\s+|\s+body\s+|\s+say\s+)(.+)$", normalized, re.I)
    if not send_match:
        send_match = re.search(r"\b(?:send|email)\s+(?:to\s+)?(.+?)(?:\s+subject\s+|\s+with\s+subject\s+)(.+?)(?:\s+message\s+|\s+body\s+|\s+say\s+)(.+)$", normalized, re.I)
    if send_match:
        recipient = send_match.group(1).strip().rstrip(".")
        subject = send_match.group(2).strip().rstrip(".")
        body = send_match.group(3).strip().rstrip(".")
        if not re.search(r"@", recipient):
            display_error("Please provide a valid email address, Sir.")
            return True
        try:
            send_email(recipient, subject, body)
            display_response(f"Email sent to {recipient}, Sir.")
            speak_text(f"Email sent to {recipient}, Sir.")
        except Exception as error:
            display_error(str(error))
        return True

    if re.search(r"\b(?:mail|email)\b", normalized):
        display_response("Say send email to person@example.com subject hello message this is the note, or ask me to check my inbox, Sir.")
        return True
    return False


def refresh_dashboard():
    if dashboard_task_label is not None:
        dashboard_task_label.config(text=f"TASKS  ·  {len(tasks)} active")
    if dashboard_reminder_label is not None:
        dashboard_reminder_label.config(text=f"REMINDERS  ·  {len(reminders)} queued")
    if dashboard_event_label is not None:
        dashboard_event_label.config(text=f"CALENDAR  ·  {len(calendar_events)} events")
    if dashboard_memory_label is not None:
        dashboard_memory_label.config(text=f"MEMORY  ·  {len(memories)} saved")


def handle_memory_command(normalized):
    if re.search(r"\b(?:what(?:'s| is)? my name|who am i|who am i\?)\b", normalized):
        matches = [memory for memory in memories if memory.lower().startswith("your name is")]
        if matches:
            display_response(matches[-1].replace("Your name is ", "Your name is ", 1) if matches else "I know your name, Sir.")
        else:
            display_response("I do not know your name yet, Sir. Tell me, my name is ...")
        return True

    if re.search(r"\b(?:what do you remember|show my memories|list my memories|what do you know about me)\b", normalized):
        if memories:
            display_response("I remember, Sir:\n" + "\n".join(f"{index}. {item}" for index, item in enumerate(memories, 1)))
        else:
            display_response("I do not have any saved memories yet, Sir.")
        return True

    if re.search(r"\b(?:forget everything|clear all memories|erase all memories)\b", normalized):
        memories.clear()
        save_memories()
        apply_location_to_prompts()
        refresh_dashboard()
        display_response("All persistent memories have been erased, Sir.")
        speak_text("All persistent memories have been erased, Sir.")
        return True

    if re.search(r"\b(?:my\s+name\s+is|i am|i'm)\s+([a-zA-Z][a-zA-Z'\- ]+)$", normalized):
        name = re.search(r"\b(?:my\s+name\s+is|i am|i'm)\s+([a-zA-Z][a-zA-Z'\- ]+)$", normalized).group(1).strip().rstrip(".")
        fact = f"Your name is {name}."
        if fact.lower() not in {memory.lower() for memory in memories}:
            memories.append(fact)
            memories[:] = memories[-50:]
            save_memories()
            apply_location_to_prompts()
        refresh_dashboard()
        display_response(f"Noted, Sir. I will remember that your name is {name}.")
        return True

    pref_match = re.search(r"\b(?:my\s+favorite\s+([a-zA-Z ]+?)\s+is|favorite\s+([a-zA-Z ]+?)\s+is)\s+(.+)$", normalized)
    if pref_match:
        category = (pref_match.group(1) or pref_match.group(2) or "thing").strip().rstrip(".")
        value = pref_match.group(3).strip().rstrip(".")
        fact = f"Your favorite {category} is {value}."
        if fact.lower() not in {memory.lower() for memory in memories}:
            memories.append(fact)
            memories[:] = memories[-50:]
            save_memories()
            apply_location_to_prompts()
        refresh_dashboard()
        display_response(f"Saved your preference, Sir: {fact}")
        return True

    forget = re.search(r"\b(?:forget|delete)\s+(?:that\s+)?(.+)$", normalized)
    if forget and not re.search(r"\b(?:everything|all memories)\b", normalized):
        target = forget.group(1).strip().rstrip(".")
        removed = [item for item in memories if target in item.lower()]
        memories[:] = [item for item in memories if target not in item.lower()]
        save_memories()
        apply_location_to_prompts()
        refresh_dashboard()
        display_response(f"Forgot {len(removed)} matching memor{'y' if len(removed) == 1 else 'ies'}, Sir.")
        return True

    remember = re.search(r"\b(?:remember|save this|keep this in mind)\s+(?:that\s+)?(.+)$", normalized)
    if remember:
        item = remember.group(1).strip().rstrip(".")
        if item and item.lower() not in {memory.lower() for memory in memories}:
            memories.append(item)
            memories[:] = memories[-50:]
            save_memories()
            apply_location_to_prompts()
        refresh_dashboard()
        display_response(f"I will remember that, Sir: {item}")
        speak_text("I will remember that, Sir.")
        return True
    return False


def handle_task_command(normalized):
    if re.search(r"\b(?:show|list|what are|what's on)\b.*\b(?:my\s+)?tasks?\b", normalized):
        if not tasks:
            display_response("You do not have any active tasks, Sir.")
            return True
        lines = [f"{index}. {task['title']}" + ("  •  done" if task.get("done") else "") for index, task in enumerate(tasks, 1)]
        display_response("Current tasks, Sir:\n" + "\n".join(lines))
        return True

    if re.search(r"\b(?:clear|delete|remove all)\s+(?:my\s+)?tasks?\b", normalized):
        tasks.clear()
        save_tasks()
        refresh_dashboard()
        display_response("All tasks have been cleared, Sir.")
        return True

    done_match = re.search(r"\b(?:complete|finish|done|mark)\s+(?:task\s+)?(\d+)\b", normalized)
    if done_match:
        index = int(done_match.group(1)) - 1
        if 0 <= index < len(tasks):
            tasks[index]["done"] = True
            save_tasks()
            refresh_dashboard()
            display_response(f"Task {index + 1} marked complete, Sir: {tasks[index]['title']}")
        else:
            display_response("That task number does not exist, Sir.")
        return True

    remove_match = re.search(r"\b(?:remove|delete)\s+(?:task\s+)?(\d+)\b", normalized)
    if remove_match:
        index = int(remove_match.group(1)) - 1
        if 0 <= index < len(tasks):
            removed = tasks.pop(index)
            save_tasks()
            refresh_dashboard()
            display_response(f"Removed task {index + 1}, Sir: {removed['title']}")
        else:
            display_response("That task number does not exist, Sir.")
        return True

    add_match = re.search(r"\b(?:add|new|create)\s+(?:a\s+)?(?:task|todo|to do)\s*(?:for\s+)?(.+)$", normalized)
    if add_match:
        title = add_match.group(1).strip().rstrip(".")
        if not title:
            display_response("Please give me a task to add, Sir.")
            return True
        tasks.append({"title": title, "done": False})
        save_tasks()
        refresh_dashboard()
        display_response(f"Task added, Sir: {title}")
        speak_text(f"Task added, Sir: {title}")
        return True

    if re.search(r"\b(?:task|to do|todo)\b", normalized):
        display_response("Say add task followed by the task, or ask me to list tasks, Sir.")
        return True
    return False


def export_chat():
    if chat_area is None:
        return
    content = chat_area.get("1.0", tk.END).strip()
    if not content:
        display_response("There is no conversation to export, Sir.")
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = filedialog.asksaveasfilename(
        title="Export JARVIS conversation",
        initialdir=BASE_DIR,
        initialfile=f"jarvis_conversation_{timestamp}.txt",
        defaultextension=".txt",
        filetypes=[("Text file", "*.txt"), ("JSON file", "*.json")],
    )
    if not path:
        return
    try:
        if path.lower().endswith(".json"):
            payload = {
                "exported_at": datetime.now().isoformat(timespec="seconds"),
                "model": JARVIS_MODEL,
                "mode": current_mode,
                "conversation": content,
            }
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=True)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"J.A.R.V.I.S. CONVERSATION EXPORT\nExported: {datetime.now().isoformat(timespec='seconds')}\n\n{content}\n")
        display_response(f"Conversation exported successfully, Sir.\nSaved to: {path}")
        speak_text("Conversation exported successfully, Sir.")
    except OSError as error:
        display_error(f"Could not export the conversation: {error}")


def handle_export_command(normalized):
    if re.search(r"\b(?:export|save)\s+(?:this\s+)?(?:chat|conversation|session)\b", normalized):
        export_chat()
        return True
    return False


def search_personal_files(query):
    query = query.strip().lower()
    folders = ("Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos")
    roots = [os.path.join(os.path.expanduser("~"), folder) for folder in folders]
    matches = []
    for search_root in roots:
        if not os.path.isdir(search_root):
            continue
        for current_root, directories, filenames in os.walk(search_root):
            directories[:] = [name for name in directories if name not in {"node_modules", ".git", "__pycache__"}]
            for filename in filenames:
                if query in filename.lower():
                    matches.append(os.path.join(current_root, filename))
                    if len(matches) >= 25:
                        return matches
    return matches


def handle_file_search_command(normalized):
    if re.search(r"\b(?:new\s+tab|online|web|google|youtube)\b", normalized):
        return False
    search = re.search(
        r"\b(?:find|search for|look for|where is)\s+(?:the\s+)?(?:file|folder|document)?\s*(.+)$",
        normalized,
    )
    if not search:
        return False
    query = search.group(1).strip().rstrip(".")
    if query in {"a file", "files", "my files", "something"}:
        display_response("Please tell me the file name or part of its name, Sir.")
        return True
    display_response(f"Searching your personal folders for {query}, Sir.")

    def worker():
        matches = search_personal_files(query)
        if matches:
            response = "I found these files, Sir:\n" + "\n".join(
                f"{index}. {path}" for index, path in enumerate(matches, 1)
            )
        else:
            response = f"I could not find a file matching {query}, Sir."
        if root:
            root.after(0, display_response, response)
            root.after(0, speak_text, f"File search complete. {len(matches)} match{'es' if len(matches) != 1 else ''} found, Sir.")

    threading.Thread(target=worker, daemon=True).start()
    return True


def open_browser_target(target):
    cleaned = (target or "").strip().rstrip(".")
    if not cleaned:
        return False
    if re.search(r"\b(?:youtube|google)\s+(?:and\s+)?(?:search|look\s+up|find)\s+(?:for\s+)?(.+)$", cleaned, re.I):
        match = re.search(r"\b(?:youtube|google)\s+(?:and\s+)?(?:search|look\s+up|find)\s+(?:for\s+)?(.+)$", cleaned, re.I)
        query = match.group(1).strip()
        site = re.search(r"\b(youtube|google)\b", cleaned, re.I).group(1).lower()
        if site == "youtube":
            webbrowser.open("https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query))
        else:
            webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(query))
        return True
    if cleaned.startswith(("http://", "https://")):
        webbrowser.open(cleaned)
        return True
    if re.search(r"\.[a-z]{2,}(?:/|$)", cleaned):
        url = cleaned if cleaned.startswith("http") else "https://" + cleaned
        webbrowser.open(url)
        return True
    common_sites = {
        "google": "https://www.google.com",
        "youtube": "https://www.youtube.com",
        "gmail": "https://mail.google.com",
        "github": "https://github.com",
        "chatgpt": "https://chatgpt.com",
        "facebook": "https://facebook.com",
        "instagram": "https://instagram.com",
        "twitter": "https://x.com",
        "linkedin": "https://linkedin.com",
        "reddit": "https://reddit.com",
    }
    lower = cleaned.lower()
    if lower in common_sites:
        webbrowser.open(common_sites[lower])
        return True
    webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(cleaned))
    return True


def open_youtube_result(query, result_number=1):
    query = (query or "").strip()
    if not query:
        return False
    try:
        from urllib.request import Request, urlopen
        from urllib.parse import quote_plus
        search_url = "https://www.youtube.com/results?search_query=" + quote_plus(query)
        req = Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=15) as response:
            html = response.read().decode("utf-8", "ignore")
        pattern = r"/watch\?v=([A-Za-z0-9_-]{11})"
        matches = re.findall(pattern, html)
        if not matches:
            webbrowser.open(search_url)
            return False
        matches = list(dict.fromkeys(matches))
        index = max(0, min(len(matches) - 1, int(result_number) - 1))
        selected = matches[index]
        video_url = "https://www.youtube.com/watch?v=" + selected
        webbrowser.open(video_url)
        return True
    except Exception:
        search_url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
        webbrowser.open(search_url)
        return False


def youtube_result_number(value):
    positions = {
        "first": 1, "one": 1, "1st": 1,
        "second": 2, "two": 2, "2nd": 2,
        "third": 3, "three": 3, "3rd": 3,
        "fourth": 4, "four": 4, "4th": 4,
        "fifth": 5, "five": 5, "5th": 5,
    }
    cleaned = (value or "").lower().strip()
    if cleaned in positions:
        return positions[cleaned]
    number_match = re.search(r"\d+", cleaned)
    return int(number_match.group(0)) if number_match else 1


def handle_browser_command(normalized):
    combined_site_search = re.search(
        r"\b(?:open|launch|go\s+to|visit|search|look\s+up|find)\s+(?:the\s+)?(?:on\s+)?(youtube|google)\s+(?:and\s+)?(?:search|look\s+up|find)\s+(?:for\s+)?(.+)$",
        normalized,
        re.I,
    )
    if combined_site_search:
        site = combined_site_search.group(1).lower().strip()
        query = combined_site_search.group(2).strip().rstrip(".")
        if site == "youtube":
            url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
            webbrowser.open_new_tab(url)
            display_response(f"Opening YouTube results for {query}, Sir.")
            speak_text("Opening the YouTube results now, Sir.")
        else:
            url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
            webbrowser.open_new_tab(url)
            display_response(f"Searching Google for {query}, Sir.")
            speak_text(f"Searching Google for {query}, Sir.")
        return True

    combined_site_search = re.search(
        r"\b(?:open|launch|go\s+to|visit)\s+(?:the\s+)?(youtube|google)\s+(?:and\s+)?(?:search|look\s+up|find)\s+(?:for\s+)?(.+)$",
        normalized,
        re.I,
    )
    if combined_site_search:
        site = combined_site_search.group(1).lower().strip()
        query = combined_site_search.group(2).strip().rstrip(".")
        if site == "youtube":
            url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
            webbrowser.open_new_tab(url)
            display_response(f"Opening YouTube results for {query}, Sir.")
            speak_text("Opening the YouTube results now, Sir.")
        else:
            url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
            webbrowser.open_new_tab(url)
            display_response(f"Searching Google for {query}, Sir.")
            speak_text(f"Searching Google for {query}, Sir.")
        return True

    youtube_number_match = re.search(
        r"\b(?:open|play|watch)\s+(?:the\s+)?(?:youtube\s+)?(?:video|result|link)?\s*"
        r"(first|second|third|fourth|fifth|one|two|three|four|five|\d+(?:st|nd|rd|th)?)\s*"
        r"(?:video|result|link)?\s+(?:for|of)\s+(.+?)(?:\s+(?:on|in)\s+youtube)?$",
        normalized,
        re.I,
    )
    if youtube_number_match:
        result_number = youtube_result_number(youtube_number_match.group(1))
        query = youtube_number_match.group(2).strip().rstrip(".")
        if open_youtube_result(query, result_number):
            display_response(f"Opening YouTube result {result_number} for {query}, Sir.")
            speak_text(f"Opening YouTube result {result_number} for {query}, Sir.")
            return True

    youtube_number_match = re.search(r"\b(?:open|play|watch)\s+(?:youtube\s+)?(?:video\s+)?(\d+)\s+(?:for\s+)?(.+)$", normalized, re.I)
    if youtube_number_match:
        result_number = int(youtube_number_match.group(1))
        query = youtube_number_match.group(2).strip().rstrip(".")
        if open_youtube_result(query, result_number):
            display_response(f"Opening YouTube result {result_number} for {query}, Sir.")
            speak_text(f"Opening YouTube result {result_number} for {query}, Sir.")
            return True

    youtube_match = re.search(r"\b(?:open|play|watch|search)\s+(?:for\s+)?(.+?)\s+(?:on|in)\s+youtube\b", normalized, re.I)
    if youtube_match:
        query = youtube_match.group(1).strip().rstrip(".")
        if open_youtube_result(query, 1):
            display_response(f"Opening YouTube for {query}, Sir.")
            speak_text(f"Opening YouTube for {query}, Sir.")
            return True

    site_open = re.search(r"\b(?:open|go to|launch|visit)\s+(?:the\s+)?(.+)$", normalized)
    if site_open:
        target = site_open.group(1).strip()
        if open_browser_target(target):
            display_response(f"Opening {target} in the browser, Sir.")
            speak_text(f"Opening {target} now, Sir.")
            return True

    search_match = re.search(r"\b(?:search(?:\s+(?:the\s+)?(?:web|google))?(?:\s+for)?|look up|find)\s+(.+)$", normalized)
    if search_match:
        target = search_match.group(1).strip().rstrip(".")
        query = target
        if " on " in query.lower():
            query = re.split(r"\s+on\s+", query, flags=re.I)[0].strip()
        webbrowser.open("https://www.google.com/search?q=" + urllib.parse.quote_plus(query))
        display_response(f"Searching the web for {query}, Sir.")
        speak_text(f"Searching the web for {query}, Sir.")
        return True

    return False


def send_media_key(key_code):
    if not sys.platform.startswith("win"):
        return False
    ctypes.windll.user32.keybd_event(key_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(key_code, 0, 2, 0)
    return True


def handle_system_control_command(normalized):
    media_actions = {
        "volume up": (0xAF, "Volume increased, Sir."),
        "turn volume up": (0xAF, "Volume increased, Sir."),
        "volume down": (0xAE, "Volume decreased, Sir."),
        "turn volume down": (0xAE, "Volume decreased, Sir."),
        "mute": (0xAD, "Volume muted, Sir."),
        "mute volume": (0xAD, "Volume muted, Sir."),
        "unmute": (0xAD, "Volume toggled, Sir."),
        "play music": (0xB3, "Playback toggled, Sir."),
        "pause music": (0xB3, "Playback toggled, Sir."),
        "pause": (0xB3, "Playback toggled, Sir."),
    }
    for phrase, (key_code, response) in media_actions.items():
        if re.search(rf"\b{re.escape(phrase)}\b", normalized):
            if send_media_key(key_code):
                display_response(response)
                speak_text(response)
            return True

    settings = {
        "wifi": "ms-settings:network-wifi",
        "wi-fi": "ms-settings:network-wifi",
        "bluetooth": "ms-settings:bluetooth",
        "display settings": "ms-settings:display",
        "screen settings": "ms-settings:display",
        "sound settings": "ms-settings:sound",
        "settings": "ms-settings:",
    }
    for phrase, target in settings.items():
        if re.search(rf"\b(?:open|show|go to)\s+(?:my\s+)?{re.escape(phrase)}(?:\s+settings)?\b", normalized):
            os.startfile(target)
            display_response(f"Opening {phrase} settings, Sir.")
            return True

    if re.search(r"\b(?:show|list)\s+(?:running\s+)?(?:processes|tasks|programs)\b", normalized):
        result = subprocess.run(["tasklist", "/fo", "csv", "/nh"], capture_output=True, text=True, check=False)
        process_names = []
        for line in result.stdout.splitlines():
            fields = line.split('","')
            if fields and fields[0].startswith('"'):
                process_names.append(fields[0].strip('"'))
        unique_names = list(dict.fromkeys(process_names))[:15]
        display_response("Running processes, Sir:\n" + "\n".join(unique_names))
        return True
    return False


def assistant_help_summary():
    return (
        "My active command set, Sir:\n"
        "- Tasks: add task, list tasks, mark task done, remove task\n"
        "- Browser: open google, open youtube, search for anything\n"
        "- Files: open my documents, open downloads, find a file\n"
        "- Reminders: set reminder in 10 minutes, list reminders\n"
        "- Calendar: add event, show calendar\n"
        "- Email: check inbox, send email to person@example.com subject hello message body\n"
        "- System: volume up, open settings, shutdown, restart, lock screen\n"
        "- Context: repeat, status, help"
    )


def handle_context_commands(normalized):
    if re.search(r"\b(?:help|what can you do|show commands|command list)\b", normalized):
        response = assistant_help_summary()
        display_response(response)
        speak_text(response)
        return True

    if re.search(r"\b(?:repeat|say again|what did you say)\b", normalized):
        response = last_response_text or "I have not spoken yet, Sir."
        display_response(response)
        speak_text(response)
        return True

    if re.search(r"\b(?:status|state|report)\b", normalized):
        task_count = len(tasks)
        reminder_count = len(reminders)
        event_count = len(calendar_events)
        mode_text = current_mode.upper()
        response = (
            f"Current status, Sir:\n"
            f"- Mode: {mode_text}\n"
            f"- Tasks: {task_count}\n"
            f"- Reminders: {reminder_count}\n"
            f"- Calendar events: {event_count}\n"
            f"- Location: {location_info.get('city') or 'Unknown'}"
        )
        display_response(response)
        return True

    if re.search(r"\b(?:take note|note this|remember this)\b", normalized):
        capture = re.search(r"\b(?:take note|note this|remember this)\s+(.+)$", normalized)
        if capture:
            item = capture.group(1).strip().rstrip(".")
            if item:
                memories.append(item)
                memories[:] = memories[-50:]
                save_memories()
                apply_location_to_prompts()
                refresh_dashboard()
                display_response(f"Saved a note, Sir: {item}")
                return True

    return False


def normalize_command_shorthand(text):
    normalized = " ".join((text or "").lower().split()).strip()
    if not normalized:
        return normalized
    for _ in range(3):
        normalized = re.sub(r"^(?:hey\s+)?(?:jarvis[,.]?\s+)?(?:can|could|would|will)\s+you\s+", "", normalized)
        normalized = re.sub(r"^(?:please|just|kindly)\s+", "", normalized)
    normalized = re.sub(r"(?:\s+(?:please|for\s+me))+$", "", normalized)
    normalized = re.sub(r"\byou\s+tube\b", "youtube", normalized)
    normalized = re.sub(r"\bface\s+book\b", "facebook", normalized)
    normalized = re.sub(r"\binsta\s+gram\b", "instagram", normalized)
    normalized = re.sub(r"^(?:task|todo|to do)\s+", "add task ", normalized)
    normalized = re.sub(r"^(?:event|meeting|appointment)\s+", "add event ", normalized)
    normalized = re.sub(r"^(?:calendar)\s+", "show calendar ", normalized)
    normalized = re.sub(r"^(?:mail|email)\s+", "check email ", normalized)
    return normalized


def handle_pc_command(text):
    """Handle explicit, local PC actions without passing them to the model."""
    normalized = normalize_command_shorthand(text)
    if not normalized:
        return False

    if handle_context_commands(normalized):
        return True

    if re.search(r"\b(?:close|exit|quit)\s+(?:all\s+)?(?:browser\s+)?tabs?\b", normalized):
        if messagebox.askyesno(
            "Close all browser tabs",
            "Close every Chrome, Edge, and Firefox window? Unsaved browser work may be lost.",
        ):
            for browser in ("chrome.exe", "msedge.exe", "firefox.exe"):
                subprocess.run(
                    ["taskkill", "/F", "/T", "/IM", browser],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            display_response("All browser windows have been closed, Sir.")
            speak_text("All browser windows have been closed, Sir.")
        else:
            display_response("Browser close cancelled, Sir.")
        return True

    super_common = {
        "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
        "documents": os.path.join(os.path.expanduser("~"), "Documents"),
        "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
        "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
        "music": os.path.join(os.path.expanduser("~"), "Music"),
        "videos": os.path.join(os.path.expanduser("~"), "Videos"),
    }
    folder_match = re.search(r"\b(?:open|show|launch|go to)\s+(?:my\s+)?(desktop|documents|downloads|pictures|music|videos)\b", normalized)
    if folder_match:
        target = super_common.get(folder_match.group(1), os.path.join(os.path.expanduser("~"), folder_match.group(1).title()))
        if os.path.exists(target):
            os.startfile(target)
            display_response(f"Opening your {folder_match.group(1)}, Sir.")
            speak_text(f"Opening your {folder_match.group(1)}, Sir.")
            return True

    close_match = re.search(r"\b(?:close|exit|quit)\s+(?:the\s+)?(.+)$", normalized)
    if close_match:
        app_name = close_match.group(1).strip().rstrip(".")
        if app_name:
            app_name = (app_name.replace(" app", "").replace("window", "").strip())
            proc_names = []
            for proc in ("notepad", "calculator", "cmd", "powershell", "chrome", "msedge", "firefox"):
                if app_name.lower() in proc:
                    proc_names.append(proc)
            for proc in proc_names:
                subprocess.run(["taskkill", "/F", "/IM", f"{proc}.exe"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                display_response(f"Closed {proc}, Sir.")
                return True
            display_response(f"I do not know which app to close for {app_name}, Sir.")
            return True

    if handle_reminder_command(normalized):
        return True

    if handle_memory_command(normalized):
        return True

    if handle_task_command(normalized):
        return True

    if handle_calendar_command(normalized):
        return True

    if handle_email_command(normalized):
        return True

    if handle_export_command(normalized):
        return True

    if handle_file_search_command(normalized):
        return True

    if handle_system_control_command(normalized):
        return True

    if handle_browser_command(normalized):
        return True

    if re.search(r"\b(?:open|launch)\s+(?:this|that|it)\b", normalized):
        display_response("What should I open, Sir? Please name the app, website, file, or folder.")
        speak_text("Please name what you would like me to open, Sir.")
        return True

    if re.search(r"\b(?:cancel|abort)\s+(?:the\s+)?shutdown\b", normalized):
        subprocess.Popen(["shutdown", "/a"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        display_response("Shutdown cancelled, Sir.")
        speak_text("Shutdown cancelled, Sir.")
        return True

    if re.search(r"\b(?:shut down|shutdown|power off|turn off)\b", normalized):
        if messagebox.askyesno("Confirm shutdown", "Shut down this PC in 30 seconds, Sir?"):
            subprocess.Popen(["shutdown", "/s", "/t", "30"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            display_response("Shutdown scheduled for 30 seconds from now, Sir. Say cancel shutdown to stop it.")
            speak_text("Shutdown scheduled, Sir.")
        return True

    if re.search(r"\b(?:lock|lock my)\s+(?:the\s+)?(?:pc|computer|screen)\b", normalized):
        subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
        return True

    if re.search(r"\b(?:restart|reboot)\s+(?:the\s+)?(?:pc|computer|system)\b", normalized):
        if messagebox.askyesno("Confirm restart", "Restart this PC in 30 seconds, Sir?"):
            subprocess.Popen(["shutdown", "/r", "/t", "30"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            display_response("Restart scheduled for 30 seconds from now, Sir.")
            speak_text("Restart scheduled, Sir.")
        return True

    youtube_search = re.search(
        r"(?:search|look up|find)\s+(?:for\s+)?(.+?)\s+(?:on|in)\s+youtube\s*$",
        normalized,
    )
    youtube_open_search = re.search(
        r"youtube(?:\s+website)?\s+(?:and\s+)?(?:search|look up|find)\s+(?:for\s+)?(.+)$",
        normalized,
    )
    youtube_search_first = re.search(
        r"(?:search|look up|find)\s+youtube\s+(?:for\s+)?(.+)$",
        normalized,
    )
    youtube_play = re.search(r"(?:play|find and play)\s+(.+?)\s+on\s+youtube\s*$", normalized)
    youtube_match = youtube_search or youtube_open_search or youtube_search_first or youtube_play
    if youtube_match:
        query = youtube_match.group(1).strip().rstrip(".")
        url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
        webbrowser.open_new_tab(url)
        display_response(f"Opening YouTube results for {query}, Sir.")
        speak_text("Opening the YouTube results now, Sir.")
        return True

    new_tab_search = re.search(
        r"\b(?:open|launch)\s+(?:a\s+)?new\s+tab(?:\s+for\s+me)?\s+(?:and\s+)?search\s+(?:for\s+)?(.+)$",
        normalized,
    )
    if new_tab_search:
        query = new_tab_search.group(1).strip().rstrip(".")
        url = "https://www.google.com/search?q=" + urllib.parse.quote_plus(query)
        webbrowser.open_new_tab(url)
        display_response(f"Opening a new tab with search results for {query}, Sir.")
        speak_text("Opening a new tab and searching now, Sir.")
        return True

    website_match = re.search(r"\b(?:open|go to|visit)\s+(?:the\s+)?(?:website\s+)?(.+)$", normalized)
    if website_match:
        target = website_match.group(1).strip().rstrip(".")
        common_sites = {
            "google": "google.com", "google search": "google.com", "youtube": "youtube.com",
            "gmail": "mail.google.com", "facebook": "facebook.com", "instagram": "instagram.com",
            "whatsapp": "web.whatsapp.com", "chatgpt": "chatgpt.com", "github": "github.com",
        }
        target = common_sites.get(target, target)
        if target.startswith(("http://", "https://")) or re.search(r"\.[a-z]{2,}(?:/|$)", target):
            url = target if target.startswith(("http://", "https://")) else "https://" + target
            webbrowser.open(url)
            display_response(f"Opening {url}, Sir.")
            speak_text("Opening it now, Sir.")
            return True

    app_match = re.search(r"\b(?:open|launch|start|run)\s+(?:the\s+)?(?:app|application|program)?\s*(.+)$", normalized)
    if app_match and not re.search(r"\b(?:file|folder|website|tab)\b", normalized):
        target = re.sub(r"\s+for(?:\s+me)?$", "", app_match.group(1).strip().rstrip("."))
        app_aliases = {
            "command prompt": "cmd.exe", "cmd": "cmd.exe", "terminal": "wt.exe",
            "powershell": "powershell.exe", "notepad": "notepad.exe", "calculator": "calc.exe",
            "calc": "calc.exe", "paint": "mspaint.exe", "file explorer": "explorer.exe",
            "task manager": "taskmgr.exe", "settings": "ms-settings:",
            "my documents": os.path.join(os.path.expanduser("~"), "Documents"),
            "documents": os.path.join(os.path.expanduser("~"), "Documents"),
            "my desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
            "desktop": os.path.join(os.path.expanduser("~"), "Desktop"),
            "downloads": os.path.join(os.path.expanduser("~"), "Downloads"),
            "pictures": os.path.join(os.path.expanduser("~"), "Pictures"),
            "music": os.path.join(os.path.expanduser("~"), "Music"),
            "videos": os.path.join(os.path.expanduser("~"), "Videos"),
        }
        executable = app_aliases.get(target, target)
        if os.path.exists(executable) or shutil.which(executable):
            subprocess.Popen([executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            display_response(f"Launching {target}, Sir.")
            speak_text(f"Launching {target}, Sir.")
            return True

        app_env = os.environ.copy()
        app_env["JARVIS_APP_SEARCH"] = target
        app_query = (
            "$apps = Get-StartApps | Where-Object { $_.Name -like ('*' + $env:JARVIS_APP_SEARCH + '*') }; "
            "if ($apps) { $apps | Select-Object -First 1 -ExpandProperty AppID }"
        )
        result = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", app_query],
            capture_output=True, text=True, timeout=8, env=app_env,
        )
        app_id = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
        if app_id:
            subprocess.Popen(["explorer.exe", f"shell:AppsFolder\\{app_id}"])
            display_response(f"Launching {target}, Sir.")
            speak_text(f"Launching {target}, Sir.")
            if target in {"minecraft", "minecraft launcher"}:
                root.after(12000, select_minecraft_play)
        else:
            display_error(f"I could not find an installed app named {target}, Sir.")
        return True

    file_match = re.search(r"\b(?:open|launch)\s+(?:the\s+)?(?:file|folder)?\s*(.+)$", normalized)
    if file_match:
        target = _pc_target_path(file_match.group(1))
        if os.path.exists(target):
            os.startfile(target)
            display_response(f"Opening {target}, Sir.")
        else:
            display_error(f"I could not find that file or folder: {target}")
        return True
    return False


def is_chess_request(text):
    normalized = " ".join((text or "").lower().split())
    return bool(re.search(r"\b(?:play|start|begin|open)\b.*\bchess\b|\bchess\b.*\b(?:game|match)\b", normalized))


def is_ai_chess_request(text):
    normalized = " ".join((text or "").lower().split())
    return bool(re.search(r"\b(?:jarvis\s+vs\s+ultron|ultron\s+vs\s+jarvis|ai\s+vs\s+ai)\b", normalized))


def is_ultron_request(text):
    normalized = " ".join((text or "").lower().split())
    return bool(re.search(r"\b(?:switch|change|activate|enable|use|start)\b.*\bultron\b|\bultron\s+mode\b", normalized))


def is_ultron_help_request(text):
    normalized = " ".join((text or "").lower().split())
    return normalized in {"ultron help", "help ultron", "what can ultron do", "ultron commands"}


def ultron_help():
    display_response(
        "ULTRON assistance online, Sir.\n\n"
        "Chess: play chess · show 3D chess · hint · show board\n"
        "Difficulty: set chess difficulty easy, medium, or hard\n"
        "Analysis: rate my game · resign · stop chess",
        "ULTRON",
    )


def is_3d_chess_request(text):
    normalized = " ".join((text or "").lower().split())
    return bool(re.search(r"\b(?:3d|three dimensional|three-dimensional)\b.*\bchess\b|\bchess\b.*\b(?:3d|three dimensional|three-dimensional)\b", normalized))


def _open_3d_chess_viewer():
    """Open a local, Meshy-free 3D chessboard in the browser."""
    folder = os.path.join(BASE_DIR, "jarvis_3d_models")
    os.makedirs(folder, exist_ok=True)
    filename = "jarvis_3d_chess.html"
    path = os.path.join(folder, filename)
    html = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JARVIS 3D // CHESS</title><script type="importmap">{"imports":{"three":"https://unpkg.com/three@0.170.0/build/three.module.js","three/addons/":"https://unpkg.com/three@0.170.0/examples/jsm/"}}</script>
<style>html,body{margin:0;width:100%;height:100%;overflow:hidden;background:#02060a;color:#dffcff;font-family:Consolas,monospace}header{height:54px;display:flex;align-items:center;padding:0 18px;box-sizing:border-box;border-bottom:1px solid #00a8b8;background:#050a0f}.title{color:#00ffff;font-weight:bold;letter-spacing:2px}.hint{margin-left:auto;color:#6b858d;font-size:12px}canvas{display:block}</style></head>
<body><header><div class="title">J.A.R.V.I.S. // 3D CHESS CORE</div><div id="status" class="hint">YOUR TURN · CLICK A WHITE PIECE</div></header><script type="module">
import * as THREE from 'three'; import {OrbitControls} from 'three/addons/controls/OrbitControls.js'; import {Chess} from 'https://cdn.jsdelivr.net/npm/chess.js@1.4.0/+esm';
const scene=new THREE.Scene(); scene.background=new THREE.Color(0x02060a); const camera=new THREE.PerspectiveCamera(38,innerWidth/(innerHeight-54),.1,100); camera.position.set(7,9,10);
const renderer=new THREE.WebGLRenderer({antialias:true}); renderer.setPixelRatio(devicePixelRatio); renderer.setSize(innerWidth,innerHeight-54); document.body.appendChild(renderer.domElement); scene.add(new THREE.HemisphereLight(0xb8faff,0x081018,2.4)); const light=new THREE.DirectionalLight(0x00ffff,3); light.position.set(4,9,5); scene.add(light);
const board=new THREE.Group(); scene.add(board); const lightSquare=new THREE.MeshStandardMaterial({color:0xb9d8d5,metalness:.25,roughness:.5}); const darkSquare=new THREE.MeshStandardMaterial({color:0x12606a,metalness:.4,roughness:.35});
for(let row=0;row<8;row++)for(let col=0;col<8;col++){const tile=new THREE.Mesh(new THREE.BoxGeometry(1,.22,1),(row+col)%2?darkSquare:lightSquare);tile.position.set(col-3.5,0,row-3.5);tile.userData.square=String.fromCharCode(97+col)+(8-row);board.add(tile)}
const white=new THREE.MeshStandardMaterial({color:0xe8f6f8,metalness:.7,roughness:.22}); const black=new THREE.MeshStandardMaterial({color:0x15242a,metalness:.8,roughness:.2});
function piece(type,color){const group=new THREE.Group();const mat=color==='w'?white:black;const base=new THREE.Mesh(new THREE.CylinderGeometry(.3,.38,.18,20),mat);base.position.y=.2;group.add(base);let body;if(type==='p')body=new THREE.Mesh(new THREE.SphereGeometry(.23,16,10),mat);else if(type==='r')body=new THREE.Mesh(new THREE.CylinderGeometry(.25,.3,.75,12),mat);else if(type==='b')body=new THREE.Mesh(new THREE.ConeGeometry(.28,.9,16),mat);else if(type==='n')body=new THREE.Mesh(new THREE.ConeGeometry(.3,.75,4),mat);else if(type==='q')body=new THREE.Mesh(new THREE.CylinderGeometry(.18,.3,1.05,12),mat);else body=new THREE.Mesh(new THREE.CylinderGeometry(.22,.34,1.15,12),mat);body.position.y=.62;group.add(body);return group}
const game=new Chess(); const models=new Map(); const rows=['rnbqkbnr','pppppppp','........','........','........','........','PPPPPPPP','RNBQKBNR']; for(let row=0;row<8;row++)for(let col=0;col<8;col++){const value=rows[row][col];if(value!=='.'){const color=value===value.toUpperCase()?'w':'b';const square=String.fromCharCode(97+col)+(8-row);const model=piece(value.toLowerCase(),color);model.position.set(col-3.5,.12,row-3.5);model.userData.square=square;model.userData.color=color;models.set(square,model);board.add(model)}}
const frame=new THREE.Mesh(new THREE.BoxGeometry(8.5,.35,8.5),new THREE.MeshStandardMaterial({color:0x06343d,metalness:.6,roughness:.3})); frame.position.y=-.25; scene.add(frame); const controls=new OrbitControls(camera,renderer.domElement);controls.enableDamping=true; const raycaster=new THREE.Raycaster(); const pointer=new THREE.Vector2(); let selected=null; let thinking=false; const status=document.getElementById('status'); window.addEventListener('error',event=>{status.textContent='VIEWER ERROR · '+event.message;status.style.color='#ff5361';});
function squarePosition(square){return new THREE.Vector3(square.charCodeAt(0)-97-3.5,.12,7-(Number(square[1])-1)-3.5)} function clearHighlights(){board.children.filter(item=>item.userData.highlight).forEach(item=>board.remove(item))} function highlightMoves(){clearHighlights();for(const move of game.moves({square:selected,verbose:true})){const marker=new THREE.Mesh(new THREE.CylinderGeometry(.13,.13,.04,16),new THREE.MeshBasicMaterial({color:0x39ff88}));marker.position.set(move.to.charCodeAt(0)-97-3.5,.17,7-(Number(move.to[1])-1)-3.5);marker.userData.highlight=true;board.add(marker)}}
function animateReply(move,done){const model=models.get(move.from);if(!model){done();return}const start=model.position.clone(),end=squarePosition(move.to);let step=0;function tick(){step++;model.position.lerpVectors(start,end,step/14);if(step<14)requestAnimationFrame(tick);else done()}tick()}
function makeMove(square){if(thinking||!selected)return;const move=game.moves({square:selected,verbose:true}).find(item=>item.to===square);if(!move){selected=null;clearHighlights();status.textContent='YOUR TURN · SELECT A WHITE PIECE';return}game.move(move);const model=models.get(move.from);models.delete(move.from);if(models.has(move.to))board.remove(models.get(move.to));model.position.copy(squarePosition(move.to));model.userData.square=move.to;models.set(move.to,model);selected=null;clearHighlights();if(game.isGameOver()){status.textContent=game.isCheckmate()?'CHECKMATE · YOU WIN':'GAME OVER';return}thinking=true;status.textContent='JARVIS IS THINKING...';setTimeout(()=>{const replies=game.moves({verbose:true});const reply=replies[Math.floor(Math.random()*replies.length)];game.move(reply);const enemy=models.get(reply.from);models.delete(reply.from);if(models.has(reply.to))board.remove(models.get(reply.to));animateReply(reply,()=>{enemy.userData.square=reply.to;models.set(reply.to,enemy);thinking=false;status.textContent=game.isCheckmate()?'CHECKMATE · JARVIS WINS':(game.isCheck()?'CHECK · YOUR TURN':'YOUR TURN · SELECT A WHITE PIECE')})},700)}
renderer.domElement.addEventListener('pointerdown',event=>{pointer.x=event.clientX/innerWidth*2-1;pointer.y=-(event.clientY-54)/(innerHeight-54)*2+1;raycaster.setFromCamera(pointer,camera);const hits=raycaster.intersectObjects(board.children,true);const target=hits.find(hit=>hit.object.userData.square||hit.object.parent?.userData.square);if(!target)return;const square=target.object.userData.square||target.object.parent.userData.square;if(!selected){const pieceModel=models.get(square);if(pieceModel?.userData.color==='w'){selected=square;highlightMoves();status.textContent='SELECT DESTINATION';}}else makeMove(square)});
function animate(){requestAnimationFrame(animate);board.rotation.y+=.002;controls.update();renderer.render(scene,camera)}animate();addEventListener('resize',()=>{camera.aspect=innerWidth/(innerHeight-54);camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight-54)});
</script></body></html>"""
    with open(path, "w", encoding="utf-8") as model_file:
        model_file.write(html)
    port = _find_free_port()
    import http.server
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
    def handler_factory(*args, **kwargs):
        return QuietHandler(*args, directory=folder, **kwargs)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler_factory)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}/{filename}?v={time.time_ns()}")
    return path


def _chess_board_text():
    return chess_board.unicode(borders=True, empty_square="·")


def _chess_material_score(board):
    values = {chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 20000}
    return sum((1 if piece.color == chess.BLACK else -1) * values[piece.piece_type] for piece in board.piece_map().values())


def _chess_search_score(board, depth, alpha=-float("inf"), beta=float("inf")):
    if board.is_checkmate():
        return -100000 - depth if board.turn == chess.BLACK else 100000 + depth
    if board.is_game_over() or depth == 0:
        return _chess_material_score(board)
    maximizing = board.turn == chess.BLACK
    moves = sorted(board.legal_moves, key=lambda move: board.is_capture(move) or board.gives_check(move), reverse=True)
    if maximizing:
        score = -float("inf")
        for move in moves:
            board.push(move)
            score = max(score, _chess_search_score(board, depth - 1, alpha, beta))
            board.pop()
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return score
    score = float("inf")
    for move in moves:
        board.push(move)
        score = min(score, _chess_search_score(board, depth - 1, alpha, beta))
        board.pop()
        beta = min(beta, score)
        if beta <= alpha:
            break
    return score


def _choose_chess_move(board):
    """Choose JARVIS's move using configurable minimax search as Black."""
    depth = {"easy": 1, "medium": 2, "hard": 3}.get(chess_difficulty, 2)
    best_score, best_moves = -float("inf"), []
    moves = sorted(board.legal_moves, key=lambda move: board.is_capture(move) or board.gives_check(move), reverse=True)
    for move in moves:
        board.push(move)
        score = _chess_search_score(board, depth - 1)
        board.pop()
        if score > best_score:
            best_score, best_moves = score, [move]
        elif score == best_score:
            best_moves.append(move)
    return random.choice(best_moves)


def _choose_white_hint(board):
    """Choose the strongest available White move using the same search engine."""
    depth = {"easy": 1, "medium": 2, "hard": 3}.get(chess_difficulty, 2)
    best_score, best_moves = float("inf"), []
    for move in board.legal_moves:
        board.push(move)
        score = _chess_search_score(board, depth - 1)
        board.pop()
        if score < best_score:
            best_score, best_moves = score, [move]
        elif score == best_score:
            best_moves.append(move)
    return random.choice(best_moves)


def _chess_status():
    if chess_board.is_checkmate():
        return "CHECKMATE"
    if chess_board.is_stalemate():
        return "STALEMATE"
    if chess_board.is_insufficient_material():
        return "DRAW: INSUFFICIENT MATERIAL"
    if chess_board.is_check():
        return "CHECK"
    return "YOUR TURN" if chess_board.turn == chess.WHITE else "JARVIS'S TURN"


def rate_chess_game():
    """Give White a simple 1-10 performance rating from the current game."""
    if chess_board is None:
        return "There is no chess game to rate yet, Sir."
    values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}
    material = sum((1 if piece.color == chess.WHITE else -1) * values[piece.piece_type] for piece in chess_board.piece_map().values())
    white_moves = list(chess_board.move_stack[::2])
    captures = 0
    checks = 0
    castled = 0
    replay = chess.Board()
    for move in chess_board.move_stack:
        if replay.turn == chess.WHITE:
            captures += replay.is_capture(move)
            if replay.gives_check(move):
                checks += 1
            if replay.is_castling(move):
                castled += 1
        replay.push(move)
    rating = 5.0 + material * 0.35 + min(captures, 4) * 0.25 + min(checks, 3) * 0.35 + castled * 0.5
    result = "Game in progress"
    if chess_board.is_checkmate():
        result = "You won by checkmate" if chess_board.turn == chess.BLACK else "JARVIS won by checkmate"
        rating += 2.5 if chess_board.turn == chess.BLACK else -2.0
    elif chess_board.is_stalemate() or chess_board.is_insufficient_material():
        result = "Draw"
    rating = max(1.0, min(10.0, rating))
    return f"Your chess rating: {rating:.1f}/10\nResult: {result}\nMoves: {len(white_moves)}  ·  Captures: {captures}  ·  Checks: {checks}"


def is_chess_question(text):
    normalized = " ".join((text or "").lower().split())
    return bool(
        "?" in normalized
        or re.match(r"^(?:what|why|how|when|where|which|can|could|should|would|explain|tell me)\b", normalized)
    )


def _chess_update_status():
    if chess_status_label and chess_board:
        status = _chess_status()
        color = RED if "CHECK" in status or "MATE" in status else (GOLD if "JARVIS" in status else GREEN)
        chess_status_label.config(text=status, fg=color)


def _draw_chess_board():
    if chess_canvas is None or chess_board is None:
        return
    chess_canvas.delete("all")
    square_size = 72
    light_color, dark_color = "#d8e8e4", "#17616a"
    selected_color = "#ffd166"
    symbols = {chess.PAWN: "♟", chess.KNIGHT: "♞", chess.BISHOP: "♝", chess.ROOK: "♜", chess.QUEEN: "♛", chess.KING: "♚"}
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            color = selected_color if square == chess_selected_square else (light_color if (row + col) % 2 == 0 else dark_color)
            x1, y1 = col * square_size, row * square_size
            chess_canvas.create_rectangle(x1, y1, x1 + square_size, y1 + square_size, fill=color, outline="#061116")
            piece = chess_board.piece_at(square)
            if chess_selected_square is not None and square in {move.to_square for move in chess_board.legal_moves if move.from_square == chess_selected_square}:
                chess_canvas.create_oval(x1 + 27, y1 + 27, x1 + 45, y1 + 45, fill="#39ff88", outline="")
            if piece:
                if not chess_animation or square != chess_animation[0]:
                    chess_canvas.create_text(x1 + square_size / 2, y1 + square_size / 2, text=symbols[piece.piece_type], font=("Segoe UI Symbol", 42), fill="#f7ffff" if piece.color else "#071116")
    if chess_animation:
        from_square, to_square, progress = chess_animation
        piece = chess_board.piece_at(from_square)
        if piece:
            from_col, from_row = chess.square_file(from_square), 7 - chess.square_rank(from_square)
            to_col, to_row = chess.square_file(to_square), 7 - chess.square_rank(to_square)
            x = (from_col + (to_col - from_col) * progress + 0.5) * square_size
            y = (from_row + (to_row - from_row) * progress + 0.5) * square_size
            chess_canvas.create_text(x, y, text=symbols[piece.piece_type], font=("Segoe UI Symbol", 42), fill="#071116")
    for index, label in enumerate("abcdefgh"):
        chess_canvas.create_text(index * square_size + 8, 8 * square_size - 9, text=label, anchor="sw", font=(FONT, 9, "bold"), fill="#061116")
    for index, label in enumerate("87654321"):
        chess_canvas.create_text(5, index * square_size + 8, text=label, anchor="nw", font=(FONT, 9, "bold"), fill="#061116")
    _chess_update_status()


def _close_chess_window():
    global chess_active, chess_window, chess_canvas, chess_selected_square, chess_status_label, chess_animation, chess_thinking, chess_ai_battle
    chess_active = False
    chess_thinking = False
    chess_ai_battle = False
    chess_selected_square = None
    chess_animation = None
    if chess_window:
        chess_window.destroy()
    chess_window = chess_canvas = chess_status_label = None


def _animate_chess_reply(reply, user_san, step=0):
    global chess_animation, chess_thinking, chess_active
    if not chess_window or not chess_active:
        chess_thinking = False
        return
    progress = min(1.0, step / 12)
    chess_animation = (reply.from_square, reply.to_square, progress)
    _draw_chess_board()
    if progress < 1.0:
        chess_window.after(90, _animate_chess_reply, reply, user_san, step + 1)
        return
    chess_animation = None
    reply_san = chess_board.san(reply)
    chess_board.push(reply)
    chess_thinking = False
    if chess_ai_battle:
        display_response(f"{user_san}: {reply_san}\n\n{_chess_board_text()}\n\n{_chess_status()}")
        if chess_board.is_game_over():
            display_response(rate_chess_game())
            chess_active = False
        elif chess_window:
            chess_window.after(900, _run_ai_battle_turn)
        _draw_chess_board()
        return
    rating = f"\n\n{rate_chess_game()}" if chess_board.is_game_over() else ""
    display_response(f"Your move: {user_san}\nJARVIS: {reply_san}\n\n{_chess_board_text()}\n\n{_chess_status()}{rating}")
    if chess_board.is_game_over():
        chess_active = False
    _draw_chess_board()


def _run_ai_battle_turn():
    global chess_thinking
    if not chess_active or not chess_ai_battle or chess_board.is_game_over():
        return
    player = "JARVIS" if chess_board.turn == chess.WHITE else "ULTRON"
    reply = _choose_white_hint(chess_board) if chess_board.turn == chess.WHITE else _choose_chess_move(chess_board)
    chess_thinking = True
    if chess_status_label:
        chess_status_label.config(text=f"{player} IS THINKING...", fg=GOLD)
    chess_window.after(700, _animate_chess_reply, reply, player)


def _chess_square_click(event):
    global chess_selected_square, chess_active, chess_thinking
    if not chess_active or chess_thinking or chess_ai_battle:
        return
    square_size = 72
    col, row = event.x // square_size, event.y // square_size
    if not (0 <= col < 8 and 0 <= row < 8):
        return
    square = chess.square(col, 7 - row)
    if chess_selected_square is None:
        piece = chess_board.piece_at(square)
        if piece and piece.color == chess.WHITE:
            chess_selected_square = square
            _draw_chess_board()
        return
    move = chess.Move(chess_selected_square, square)
    if move not in chess_board.legal_moves:
        promotion = chess.Move(chess_selected_square, square, promotion=chess.QUEEN)
        if promotion in chess_board.legal_moves:
            move = promotion
        else:
            chess_selected_square = None
            _draw_chess_board()
            return
    user_san = chess_board.san(move)
    chess_board.push(move)
    chess_selected_square = None
    if not chess_board.is_game_over():
        reply = _choose_chess_move(chess_board)
        chess_thinking = True
        if chess_status_label:
            chess_status_label.config(text="JARVIS IS THINKING...", fg=GOLD)
        chess_window.after(350, _animate_chess_reply, reply, user_san)
    else:
        display_response(f"Your move: {user_san}\n\n{_chess_board_text()}\n\n{_chess_status()} Game over, Sir.")
        chess_active = False
    _draw_chess_board()


def _open_2d_chess_board():
    global chess_window, chess_canvas, chess_status_label
    if chess_window:
        chess_window.lift()
        return
    chess_window = tk.Toplevel(root)
    chess_window.title("J.A.R.V.I.S. // INTERACTIVE CHESS")
    chess_window.configure(bg=BG)
    chess_window.resizable(False, False)
    tk.Label(chess_window, text="J.A.R.V.I.S. // INTERACTIVE CHESS", bg=BG, fg=MAGENTA, font=(FONT, 13, "bold")).pack(pady=(12, 4))
    tk.Label(chess_window, text="You are White  ·  click a piece, then click its destination", bg=BG, fg=MUTED, font=(FONT, 9)).pack(pady=(0, 10))
    chess_status_label = tk.Label(chess_window, text="YOUR TURN", bg=BG, fg=GREEN, font=(FONT, 10, "bold"))
    chess_status_label.pack(pady=(0, 8))
    chess_canvas = tk.Canvas(chess_window, width=576, height=576, bg=BG, highlightthickness=1, highlightbackground=MAGENTA)
    chess_canvas.pack(padx=12)
    chess_canvas.bind("<Button-1>", _chess_square_click)
    tk.Button(chess_window, text="END GAME", command=_close_chess_window, bg=PANEL2, fg=MAGENTA, relief=tk.FLAT, font=(FONT, 9, "bold")).pack(pady=10)
    chess_window.protocol("WM_DELETE_WINDOW", _close_chess_window)
    _draw_chess_board()


def start_chess_game():
    global chess_board, chess_active, chess_ai_battle
    if chess is None:
        display_error("Chess support is not installed. Run: python -m pip install python-chess")
        return True
    chess_board = chess.Board()
    chess_active = True
    chess_ai_battle = False
    _open_2d_chess_board()
    response = f"Chess started, Sir. You are White. Difficulty: {chess_difficulty.upper()}. Make a move such as e2e4 or Nf3.\n\n" + _chess_board_text()
    display_response(response)
    speak_text("Chess started. You are White, Sir.")
    return True


def start_ai_chess_battle():
    global chess_board, chess_active, chess_ai_battle
    if chess is None:
        display_error("Chess support is not installed. Run: python -m pip install python-chess")
        return True
    chess_board = chess.Board()
    chess_active = chess_ai_battle = True
    _open_2d_chess_board()
    display_response(f"JARVIS versus ULTRON battle started, Sir. JARVIS is White. Difficulty: {chess_difficulty.upper()}.")
    _draw_chess_board()
    chess_window.after(700, _run_ai_battle_turn)
    return True


def handle_chess_command(text):
    global chess_active, chess_thinking, chess_difficulty
    normalized = " ".join((text or "").lower().split())
    chess_command = bool(re.search(r"\b(?:chess|checkmate|hint|resign|rate my game|review my game)\b", normalized))
    difficulty_command = bool(re.search(r"\b(?:chess\s+)?difficulty\s+(?:easy|medium|hard)\b", normalized))
    if current_mode != "ultron" and (is_chess_request(normalized) or chess_active or is_3d_chess_request(normalized) or chess_command or difficulty_command):
        display_response("Chess is available only in ULTRON mode, Sir. Say activate Ultron first.")
        return True
    difficulty_match = re.search(r"\b(?:set|change)\s+(?:chess\s+)?difficulty\s+(easy|medium|hard)\b", normalized)
    if difficulty_match:
        chess_difficulty = difficulty_match.group(1)
        display_response(f"Chess difficulty set to {chess_difficulty.upper()}, Sir.")
        return True
    if is_ai_chess_request(normalized) and not chess_active:
        return start_ai_chess_battle()
    if is_chess_request(normalized) and not chess_active:
        return start_chess_game()
    if not chess_active:
        if normalized in {"rate my game", "rate game", "review my game"}:
            display_response(rate_chess_game())
            return True
        return False
    if re.search(r"\b(?:quit|stop|exit|close|end|resign)\b", normalized):
        rating = rate_chess_game()
        _close_chess_window()
        display_response(f"Chess game ended, Sir.\n\n{rating}")
        return True
    if re.search(r"\b(?:rate|score|review)\b", normalized):
        display_response(rate_chess_game())
        return True
    if re.search(r"\b(?:hint|help|suggest)\b", normalized):
        if chess_board.turn != chess.WHITE:
            display_response("Please wait for my move to finish, Sir.")
            return True
        hint = _choose_white_hint(chess_board)
        hint_san = chess_board.san(hint)
        display_response(f"Strategic hint: I will play {hint_san} for you, Sir.")
        chess_board.push(hint)
        _draw_chess_board()
        reply = _choose_chess_move(chess_board)
        chess_thinking = True
        if chess_window:
            chess_status_label.config(text="ULTRON IS THINKING...", fg=GOLD)
            chess_window.after(700, _animate_chess_reply, reply, f"Hint move {hint_san}")
        else:
            chess_board.push(reply)
        return True
    if re.search(r"\b(?:board|position|show)\b", normalized):
        display_response(_chess_board_text())
        _draw_chess_board()
        return True
    if is_chess_question(text):
        return False
    move_text = re.sub(r"^(?:please\s+)?(?:move\s+)?", "", normalized).strip().rstrip(".!?")
    try:
        try:
            move = chess_board.parse_san(move_text)
        except ValueError:
            move = chess_board.parse_uci(move_text.replace(" ", ""))
    except ValueError:
        display_response("That is not a legal chess move, Sir. Try a move such as e2e4 or Nf3.")
        return True
    user_san = chess_board.san(move)
    chess_board.push(move)
    if chess_board.is_game_over():
        display_response(f"Your move: {user_san}\n\n{_chess_board_text()}\n\n{_chess_status()} Game over, Sir.\n\n{rate_chess_game()}")
        chess_active = False
        _draw_chess_board()
        return True
    reply = _choose_chess_move(chess_board)
    chess_thinking = True
    if chess_window:
        chess_status_label.config(text="JARVIS IS THINKING...", fg=GOLD)
        chess_window.after(350, _animate_chess_reply, reply, user_san)
    else:
        chess_board.push(reply)
        chess_thinking = False
        display_response(f"Your move: {user_san}\nJARVIS: {chess_board.san(reply)}\n\n{_chess_board_text()}\n\n{_chess_status()}")
        if chess_board.is_game_over():
            chess_active = False
    return True


def select_minecraft_play(attempt=1):
    """Activate Minecraft Launcher and click its Play control after loading."""
    if not sys.platform.startswith("win"):
        return
    try:
        user32 = ctypes.windll.user32
        window = user32.FindWindowW(None, "Minecraft Launcher")
        if not window:
            if attempt < 4:
                root.after(5000, select_minecraft_play, attempt + 1)
            else:
                display_error("Minecraft Launcher is still loading, Sir. Please click Play when it appears.")
            return
        rectangle = wintypes.RECT()
        user32.GetWindowRect(window, ctypes.byref(rectangle))
        width = rectangle.right - rectangle.left
        height = rectangle.bottom - rectangle.top
        user32.SetForegroundWindow(window)
        user32.SetCursorPos(rectangle.left + int(width * 0.52), rectangle.top + int(height * 0.72))
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
        display_response("Minecraft Launcher is ready. Selecting Play, Sir.")
        speak_text("Selecting Play now, Sir.")
    except (AttributeError, OSError) as error:
        display_error(f"Minecraft opened, but I could not select Play: {error}")


def speak_text(text, wait=False):
    global tts_busy, tts_process, tts_audio_player
    done = threading.Event()
    tts_stop_event.clear()

    def worker():
        global tts_busy, tts_process
        tts_busy = True
        try:
            if tts_stop_event.is_set():
                return
            if NATURAL_VOICE and sys.platform.startswith("win"):
                try:
                    import asyncio
                    import tempfile

                    async def synthesize():
                        output_file = tempfile.NamedTemporaryFile(prefix="jarvis_voice_", suffix=".mp3", delete=False)
                        output_path = output_file.name
                        output_file.close()
                        await edge_tts.Communicate(
                            text,
                            NATURAL_VOICE_NAME,
                            rate=NATURAL_VOICE_RATE,
                            pitch=NATURAL_VOICE_PITCH,
                            volume=NATURAL_VOICE_VOLUME,
                        ).save(output_path)
                        return output_path

                    with natural_voice_lock:
                        output_path = asyncio.run(synthesize())
                        if tts_stop_event.is_set():
                            return
                        if not pygame.mixer.get_init():
                            pygame.mixer.init()
                        tts_audio_player = pygame.mixer.music
                        tts_audio_player.load(output_path)
                        tts_audio_player.play()
                        while tts_audio_player.get_busy() and not tts_stop_event.is_set():
                            time.sleep(0.05)
                        tts_audio_player.stop()
                        tts_audio_player = None
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass
                    return
                except Exception as natural_error:
                    print("Natural voice unavailable:", natural_error)
                    return
            if sys.platform.startswith("win"):
                preferred_voices = MODE_VOICE_PROFILES.get(current_mode, MODE_VOICE_PROFILES["jarvis"])["system"]
                voice_list = ", ".join("'" + name.replace("'", "''") + "'" for name in preferred_voices)
                ps = f"""
Add-Type -AssemblyName System.Speech
$text = [Console]::In.ReadToEnd()
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$prefer = @({voice_list})
$names = @($s.GetInstalledVoices() | ForEach-Object {{ $_.VoiceInfo.Name }})
foreach ($n in $prefer) {{ if ($names -contains $n) {{ $s.SelectVoice($n); break }} }}
try {{ if ($prefer | Where-Object {{ $names -contains $_ }}) {{ $s.SelectVoice(($prefer | Where-Object {{ $names -contains $_ }})[0]) }} else {{ $s.SelectVoiceByHints([System.Speech.Synthesis.VoiceGender]::Male, [System.Speech.Synthesis.VoiceAge]::Adult, 0, [System.Globalization.CultureInfo]::GetCultureInfo('en-GB')) }} }} catch {{}}
$s.Rate = {SYSTEM_VOICE_RATE}; $s.Volume = 100
$s.Speak($text)
$s.Dispose()
"""
                if not tts_stop_event.is_set():
                    tts_process = subprocess.Popen(
                        ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                        text=True
                    )
                    tts_process.communicate(input=text)
                return
            for voice in ("en-gb+m3", "en-gb+m2", "en+m3", "en-gb", "en"):
                for binary in ("espeak-ng", "espeak"):
                    if tts_stop_event.is_set():
                        return
                    try:
                        tts_process = subprocess.Popen(
                            [binary, "-s", "138", "-p", "28", "-g", "7", "-a", "145", "-v", voice, text],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                        tts_process.wait()
                        return
                    except FileNotFoundError:
                        continue
            if not tts_stop_event.is_set():
                try:
                    tts_process = subprocess.Popen(
                        ["spd-say", "-r", "-20", "-t", "male3", text],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    tts_process.wait()
                except FileNotFoundError:
                    pass
        except Exception as e:
            if not tts_stop_event.is_set():
                print("Voice output error:", e)
        finally:
            tts_process = None
            tts_busy = False
            done.set()

    threading.Thread(target=worker, daemon=True).start()
    if wait:
        done.wait(timeout=20)


def record_pcm(seconds, sample_rate=16000):
    with mic_lock:
        audio = sd.rec(int(seconds * sample_rate), samplerate=sample_rate, channels=1, dtype="int16")
        sd.wait()
    return audio


def transcribe_pcm(audio, sample_rate=16000):
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.9
    recognizer.phrase_threshold = 0.15
    pcm = np.asarray(audio, dtype=np.int16)
    peak = int(np.max(np.abs(pcm))) if pcm.size else 0
    if peak and peak < 12000:
        pcm = np.clip(pcm.astype(np.float32) * (12000 / peak), -32767, 32767).astype(np.int16)
    return recognizer.recognize_google(
        sr.AudioData(pcm.tobytes(), sample_rate, 2), language="en-GB"
    )


def record_until_silence(chunk_seconds=0.5, min_duration=1.0, silence_window=1.2, max_duration=12.0, sample_rate=16000):
    chunks = []
    total_time = 0.0
    quiet_chunks = 0
    speaking_started = False
    while total_time < max_duration:
        chunk = record_pcm(chunk_seconds, sample_rate)
        chunks.append(chunk)
        total_time += chunk_seconds
        if audio_is_quiet(chunk):
            if speaking_started:
                quiet_chunks += 1
            else:
                quiet_chunks = 0
        else:
            speaking_started = True
            quiet_chunks = 0
        if speaking_started and total_time >= min_duration and quiet_chunks >= int(silence_window / chunk_seconds):
            break
        if total_time >= max_duration:
            break
    if not chunks:
        return np.array([], dtype=np.int16)
    return np.concatenate(chunks)


def audio_is_quiet(audio, threshold=45):
    return audio is None or len(audio) == 0 or float(np.sqrt(np.mean(audio.astype(np.float32) ** 2))) < threshold


def mode_wake_variants(mode=None):
    mode_name = (mode or current_mode or "jarvis").lower()
    return MODE_WAKE_VARIANTS.get(mode_name, MODE_WAKE_VARIANTS["jarvis"])


def mode_label(mode=None):
    return {"jarvis": "JARVIS", "vision": "VISION", "ultron": "ULTRON"}.get((mode or current_mode or "jarvis").lower(), "JARVIS")


def custom_wake_phrases(mode=None):
    mode_name = (mode or current_mode or "jarvis").lower()
    phrases = {
        "jarvis": [
            "wake up jarvis",
            "wake jarvis",
            "wake up",
            "wake up jarvis home",
            "jarvis home",
            "daddys home",
            "daddy's home",
            "dad's home",
            "dads home",
            "clap clap wake up",
            "clap clap daddys home",
            "clap clap wake up daddys home",
            "clap clap jarvis home",
            "hey jarvis",
            "good morning jarvis",
        ],
        "vision": [
            "wake up vision",
            "wake vision",
            "vision home",
            "clap clap wake up vision",
            "clap clap vision home",
            "hey vision",
            "good morning vision",
        ],
        "ultron": [
            "wake up ultron",
            "wake ultron",
            "ultron home",
            "clap clap wake up ultron",
            "clap clap ultron home",
            "hey ultron",
            "good morning ultron",
        ],
    }
    return phrases.get(mode_name, phrases["jarvis"])


def clap_detected(audio, min_peak=10000):
    """Detect one sharp clap while rejecting normal speech and room noise."""
    if audio is None or len(audio) == 0:
        return False
    pcm = np.asarray(audio, dtype=np.float32).reshape(-1)
    if pcm.size == 0:
        return False
    amplitude = np.abs(pcm)
    peak = float(np.max(amplitude))
    rms = float(np.sqrt(np.mean(np.square(pcm))))
    if peak < min_peak:
        return False
    peak_to_rms = peak / max(rms, 1.0)
    sharp_samples = float(np.count_nonzero(amplitude >= peak * 0.65)) / pcm.size
    delta = np.abs(np.diff(amplitude))
    largest_jump = float(np.max(delta)) if delta.size else 0.0
    return peak_to_rms >= 6.0 and sharp_samples <= 0.025 and largest_jump >= 6500


def detect_mode_from_wake_text(text):
    normalized = re.sub(r"[^a-z0-9' ]", " ", (text or "").lower())
    normalized = re.sub(r"\bclap\s+clap\b", " ", " ".join(normalized.split()))
    normalized = " ".join(normalized.split())
    all_modes = ["jarvis", "vision", "ultron"]
    for mode_name in all_modes:
        for phrase in custom_wake_phrases(mode_name):
            if phrase in normalized:
                return mode_name
        if mode_name in normalized:
            return mode_name
    for mode_name in all_modes:
        for variant in MODE_WAKE_VARIANTS.get(mode_name, set()):
            if re.search(rf"\b{re.escape(variant)}\b", normalized):
                return mode_name
    return None


def strip_wake_phrase(text, mode=None):
    raw = (text or "").strip()
    if not raw:
        return raw, False

    normalized = re.sub(r"[^a-z0-9' ]", " ", raw.lower())
    normalized = re.sub(r"\bclap\s+clap\b", " ", " ".join(normalized.split()))
    normalized = " ".join(normalized.split())
    if "jarevis" in normalized:
        normalized = normalized.replace("jarevis", "jarvis")
    detected_mode = detect_mode_from_wake_text(raw)
    target_mode = (mode or current_mode or 'jarvis').lower()

    for phrase in list(dict.fromkeys(phrase for mode_name in ("jarvis", "vision", "ultron") for phrase in custom_wake_phrases(mode_name))):
        if phrase in normalized:
            remainder = re.sub(r"(?i)\b(?:hey|hi|ok|okay|oi|wake(?:\s+up)?|daddys|daddy's|dad's|dads|jarvis|vision|ultron|home)\b", " ", normalized)
            remainder = " ".join(remainder.split())
            return remainder.strip(" .,!?"), True

    words = list(re.finditer(r"[a-z0-9']+", raw.lower()))
    active_variants = mode_wake_variants(mode)

    for index, word in enumerate(words):
        spoken = word.group(0).replace("'", "")
        if spoken in active_variants:
            remainder = re.sub(r"\s+", " ", raw[word.end():]).strip(" .,!? ")
            return remainder, True

        base_name = next(iter(active_variants), "jarvis")
        similarity = difflib.SequenceMatcher(None, spoken, base_name).ratio()
        has_wake_prefix = index > 0 and words[index - 1].group(0).replace("'", "") in WAKE_PREFIXES
        if similarity >= (0.68 if has_wake_prefix else 0.82):
            remainder = re.sub(r"\s+", " ", raw[word.end():]).strip(" .,!? ")
            return remainder, True
    return raw, False


def listen_voice():
    global push_to_talk_active
    if not VOICE_INPUT:
        messagebox.showerror("Voice input not installed", "python -m pip install sounddevice numpy SpeechRecognition")
        return
    push_to_talk_active = True
    set_wake_signal(100, "LISTENING")
    if listen_button:
        listen_button.config(state=tk.DISABLED, text="LISTENING...")
    status_label.config(text=f"{mode_label()}  //  LISTENING  •  SPEAK NOW", fg=GOLD)
    threading.Thread(target=listen_worker, daemon=True).start()


def listen_worker():
    global push_to_talk_active
    try:
        text = transcribe_pcm(record_until_silence())
        remainder, woke = strip_wake_phrase(text, current_mode)
        root.after(0, put_voice_text, remainder if woke and remainder else text)
    except sr.UnknownValueError:
        root.after(0, display_error, "I could not understand the speech, Sir. Please try again.")
    except Exception as e:
        root.after(0, display_error, f"Microphone error: {e}")
    finally:
        push_to_talk_active = False
        set_wake_signal(12, "SCANNING")
        root.after(0, restore_listen_button)
        root.after(0, refresh_ready_status)


def restore_listen_button():
    if listen_button:
        listen_button.config(state=tk.NORMAL, text="🎙  VOICE")


def refresh_ready_status():
    if status_label is None:
        return
    assistant_name = mode_label()
    if wake_enabled:
        status_label.config(text=f"{assistant_name}  //  ONLINE  •  READY", fg=GREEN)
    else:
        status_label.config(text=f"{assistant_name}  //  ONLINE  •  WAKE OFF", fg=GOLD)


def update_wake_button():
    if wake_button is None:
        return
    if wake_enabled:
        wake_button.config(text="●  WAKE ON", fg=GREEN, bg="#03180e")
    else:
        wake_button.config(text="○  WAKE OFF", fg=MUTED, bg=PANEL2)


def toggle_wake_mode():
    global wake_enabled
    if not VOICE_INPUT:
        messagebox.showerror("Voice input not installed", "python -m pip install sounddevice numpy SpeechRecognition")
        return
    wake_enabled = not wake_enabled
    update_wake_button()
    set_wake_signal(12 if wake_enabled else 0, "SCANNING" if wake_enabled else "OFF")
    refresh_ready_status()
    if wake_enabled:
        start_wake_listener()
        speak_text(f"Listening mode armed, Sir. Say Hey {mode_label().title()} when you need me.")
    else:
        speak_text("Listening mode disengaged, Sir.")


def start_wake_listener():
    global wake_thread_started, wake_enabled
    if not VOICE_INPUT:
        return
    wake_enabled = True
    set_wake_signal(12, "SCANNING")
    update_wake_button()
    if wake_thread_started:
        return
    wake_thread_started = True
    threading.Thread(target=wake_listener_loop, daemon=True).start()


def wake_listener_loop():
    global request_number, active_request_number
    while True:
        if root is None or not wake_enabled or push_to_talk_active:
            time.sleep(0.25)
            continue
        try:
            audio = record_pcm(2.4 if tts_busy else 5.0)
            if push_to_talk_active or not wake_enabled or audio_is_quiet(audio):
                continue

            clap = clap_detected(audio)
            if clap:
                root.after(0, set_wake_signal, 100, "CLAP DETECTED")
                root.after(0, set_listening_status, "CLAP DETECTED")
                request_number += 1
                active_request_number = request_number
                stop_speaking()
                stop_thinking()
                root.after(0, set_wake_signal, 100, "LISTENING")
                root.after(0, set_listening_status, "SPEAK YOUR ORDER NOW")
                try:
                    command = transcribe_pcm(record_until_silence())
                except sr.UnknownValueError:
                    root.after(0, refresh_ready_status)
                    root.after(0, set_wake_signal, 12, "SCANNING")
                    continue
                root.after(0, put_voice_text, command)
                root.after(0, set_wake_signal, 12, "SCANNING")
                continue

            try:
                heard = transcribe_pcm(audio)
            except sr.UnknownValueError:
                continue
            if tts_busy and is_stop_command(heard):
                root.after(0, put_voice_text, heard)
                continue
            remainder, woke = strip_wake_phrase(heard, current_mode)
            if not woke:
                continue
            detected_mode = detect_mode_from_wake_text(heard)
            wake_mode = detected_mode or current_mode
            if detected_mode and detected_mode != current_mode:
                root.after(0, switch_mode, detected_mode)
            root.after(0, set_wake_signal, 100, "WAKE DETECTED")
            root.after(0, lambda mode=wake_mode: speak_text(f"{mode_label(mode)} online, Sir."))
            request_number += 1
            active_request_number = request_number
            stop_speaking()
            stop_thinking()
            if remainder and len(remainder.split()) >= 2:
                root.after(0, set_listening_status, "COMMAND LOCKED")
                root.after(0, put_voice_text, remainder)
                time.sleep(0.2)
                continue
            root.after(0, set_listening_status, "SPEAK YOUR ORDER NOW")
            root.after(0, set_wake_signal, 100, "LISTENING")
            try:
                command = transcribe_pcm(record_until_silence())
            except sr.UnknownValueError:
                root.after(0, display_error, "I am listening, Sir, but I did not catch that order.")
                root.after(0, refresh_ready_status)
                continue
            command_clean, _ = strip_wake_phrase(command, current_mode)
            root.after(0, put_voice_text, command_clean or command)
            root.after(0, set_wake_signal, 12, "SCANNING")
        except Exception as error:
            if root and not push_to_talk_active:
                root.after(0, set_listening_status, f"WAKE CHANNEL READY  ·  {type(error).__name__}")
            time.sleep(0.6)


def set_listening_status(message):
    if status_label:
        status_label.config(text=f"{mode_label()}  //  {message}", fg=GOLD)


def set_wake_signal(level, state):
    global wake_signal_level, wake_signal_state
    wake_signal_level = max(0, min(100, int(level)))
    wake_signal_state = state


def draw_wake_signal():
    if wake_signal_canvas is None:
        return
    wake_signal_canvas.delete("all")
    width = max(20, wake_signal_canvas.winfo_width() - 4)
    pulse = 3 * math.sin(time.time() * 5) if wake_enabled and wake_signal_state == "SCANNING" else 0
    level = max(0, min(100, wake_signal_level + pulse))
    wake_signal_canvas.create_rectangle(2, 3, width + 2, 13, outline="#123846")
    color = GREEN if level >= 85 else (GOLD if level >= 45 else MUTED)
    wake_signal_canvas.create_rectangle(3, 4, 3 + width * level / 100, 12, fill=color, outline="")
    wake_signal_canvas.create_text(4, 22, anchor="sw", text=f"VOICE SIGNAL  ·  {wake_signal_state}  ·  {int(level)}%", fill=color, font=(FONT, 7, "bold"))

    if wake_enabled:
        for i in range(3):
            ring_r = 5 + i * 8 + 3 * math.sin(time.time() * 7 + i)
            x0 = width * 0.78 + (i * 4) - ring_r
            y0 = 20 - ring_r
            x1 = width * 0.78 + (i * 4) + ring_r
            y1 = 20 + ring_r
            wake_signal_canvas.create_oval(x0, y0, x1, y1, outline=color, width=1 if i == 0 else 0, tags="pulse")


def put_voice_text(text):
    input_box.delete("1.0", tk.END)
    input_box.insert("1.0", text)
    send_message()


def send_message(event=None):
    global current_attachment, current_attachment_text, current_attachment_name, request_number, active_request_number, last_user_text
    text = input_box.get("1.0", tk.END).strip()
    if not text:
        return "break"
    last_user_text = text
    input_box.delete("1.0", tk.END)
    display_user(text)
    request_number += 1
    active_request_number = request_number
    if is_jarvis_shutdown_command(text):
        shutdown_jarvis()
        return "break"
    if is_stop_command(text):
        stop_speaking()
        stop_thinking()
        refresh_ready_status()
        return "break"
    if is_wake_command(text, True) and wake_enabled:
        toggle_wake_mode()
        return "break"
    if is_wake_command(text, False) and not wake_enabled:
        toggle_wake_mode()
        return "break"
    if is_ultron_help_request(text):
        if current_mode != "ultron":
            switch_mode("ultron")
        ultron_help()
        return "break"
    if is_ultron_request(text):
        switch_mode("ultron")
        display_response("ULTRON mode activated, Sir. Tactical assistance online.", "ULTRON")
        return "break"
    if is_3d_chess_request(text) and current_mode == "ultron":
        try:
            path = _open_3d_chess_viewer()
            display_response(f"Local 3D chessboard opened without Meshy, Sir.\nSaved viewer: {path}")
        except Exception as error:
            display_error(f"3D chess viewer failed: {error}")
        return "break"
    if handle_chess_command(text):
        return "break"
    if handle_pc_command(text):
        return "break"
    if is_close_3d_request(text):
        close_3d_model_page()
        return "break"
    if is_3d_request(text) or is_simple_shape_request(text) or is_shape_collection_request(text):
        switch_mode("vision")
        generate_3d_model(text)
        return "break"
    if is_image_request(text):
        switch_mode("vision")
        generate_image(text)
        return "break"
    if not chat_titles:
        chat_titles.append(text[:35])
        history_list.insert(tk.END, text[:35])
    mode = current_mode
    request_id = request_number
    attachment = current_attachment
    attachment_text = current_attachment_text
    attachment_name = current_attachment_name
    current_attachment = current_attachment_text = current_attachment_name = None
    start_thinking()
    threading.Thread(target=ask_ollama, args=(text, mode, attachment, attachment_text, attachment_name, request_id), daemon=True).start()
    return "break"


def ask_ollama(text, mode, attachment=None, attachment_text=None, attachment_name=None, request_id=None):
    try:
        model = VISION_MODEL if mode == "vision" else JARVIS_MODEL
        msgs = vision_messages if mode == "vision" else (ultron_messages if mode == "ultron" else jarvis_messages)
        apply_location_to_prompts()
        user_content = text
        if attachment_text:
            user_content = (
                f"Attached file: {attachment_name or 'file'}\n\nFILE CONTENT:\n{attachment_text[:30000]}\n\n"
                f"USER QUESTION:\n{text}\n\nAnswer using the attached file."
            )
        user_msg = {"role": "user", "content": user_content}
        if attachment and os.path.splitext(attachment)[1].lower() in (".png", ".jpg", ".jpeg", ".webp"):
            if not os.path.isfile(attachment):
                raise RuntimeError(f"The attached image could not be found: {attachment}")
            with open(attachment, "rb") as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode("ascii")
            user_msg["images"] = [encoded_image]
            user_msg["content"] = (
                "Look carefully at the attached image and answer the user's question. "
                "Describe visible objects, people, text, colors, and important details.\n\n"
                f"USER QUESTION:\n{text}"
            )
        if mode == "vision":
            user_msg["content"] = "You are in VISION mode. Use the attachment when provided.\n\n" + user_msg["content"]
        msgs.append(user_msg)
        if attachment and mode != "vision":
            raise RuntimeError("Images can only be analyzed in VISION mode.")
        response = ollama.chat(model=model, messages=msgs)
        if request_id is not None and request_id != active_request_number:
            return
        answer = response["message"]["content"].strip()
        msgs.append({"role": "assistant", "content": answer})
        root.after(0, finish_response, answer, mode.upper())
    except Exception as e:
        error_text = str(e)
        if mode == "vision" and "gemma3:4b" in error_text.lower():
            error_text += "\n\nInstall the vision model with: ollama pull gemma3:4b"
        root.after(0, finish_error, error_text)


def finish_response(answer, label):
    stop_thinking()
    display_response(answer, label)
    if label in {"JARVIS", "VISION", "ULTRON"}:
        speak_text(answer)


def finish_error(error):
    stop_thinking()
    display_error(error)


def clear_chat():
    global jarvis_messages, vision_messages, ultron_messages, chat_titles, current_attachment, current_attachment_text, current_attachment_name
    current_attachment = current_attachment_text = current_attachment_name = None
    jarvis_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    vision_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    ultron_messages = [{"role": "system", "content": SYSTEM_PROMPT + "\nYou are ULTRON mode: tactical, concise, analytical, and focused on strategy."}]
    apply_location_to_prompts()
    chat_titles = []
    history_list.delete(0, tk.END)
    chat_area.config(state=tk.NORMAL)
    chat_area.delete("1.0", tk.END)
    chat_area.insert(tk.END, "JARVIS  ·  SYSTEM\nChannel reset. Standing by, Sir.\n", "jarvis_text")
    chat_area.config(state=tk.DISABLED)


def set_mode_voice_profile(mode="jarvis"):
    global NATURAL_VOICE_NAME, NATURAL_VOICE_RATE, NATURAL_VOICE_PITCH
    global CURRENT_MODE_VOICE_NAME, SYSTEM_VOICE_RATE
    profile = MODE_VOICE_PROFILES.get(mode, MODE_VOICE_PROFILES["jarvis"])
    NATURAL_VOICE_NAME = profile["natural"][0]
    NATURAL_VOICE_RATE = profile["rate"]
    NATURAL_VOICE_PITCH = profile["pitch"]
    CURRENT_MODE_VOICE_NAME = profile["system"][0]
    SYSTEM_VOICE_RATE = profile["system_rate"]


def switch_mode(mode):
    global current_mode, current_attachment, current_attachment_text, current_attachment_name
    current_mode = mode
    set_mode_voice_profile(mode)
    if mode == "vision":
        jarvis_button.config(bg="#031016", fg=MUTED, highlightbackground="#33444c")
        vision_button.config(bg="#140818", fg=MAGENTA, highlightbackground=MAGENTA)
        ultron_button.config(bg="#031016", fg=MUTED, highlightbackground="#33444c")
        chat_area.pack_forget()
        vision_panel.pack(fill=tk.BOTH, expand=True, padx=18, pady=(12, 8))
        status_label.config(text="VISION  //  OPTICS ONLINE  •  READY", fg=MAGENTA)
        if channel_label:
            channel_label.config(text="CHANNEL  ·  VISION / MULTIMODAL")
        if attach_button:
            attach_button.config(state=tk.NORMAL, fg=MAGENTA, highlightbackground=MAGENTA)
        if generate_button:
            generate_button.config(state=tk.NORMAL, fg=MAGENTA, highlightbackground=MAGENTA)
        if model3d_button:
            model3d_button.config(state=tk.NORMAL, fg=MAGENTA, highlightbackground=MAGENTA)
    elif mode == "ultron":
        jarvis_button.config(bg="#031016", fg=MUTED, highlightbackground="#33444c")
        vision_button.config(bg="#031016", fg=MUTED, highlightbackground="#33444c")
        ultron_button.config(bg="#261505", fg=GOLD, highlightbackground=GOLD)
        chat_area.pack_forget()
        vision_panel.pack(fill=tk.BOTH, expand=True, padx=18, pady=(12, 8))
        status_label.config(text="ULTRON  //  TACTICAL CORE ONLINE", fg=GOLD)
        channel_label.config(text="CHANNEL  ·  ULTRON / STRATEGIC")
        attach_button.config(state=tk.DISABLED, fg=MUTED)
        generate_button.config(state=tk.DISABLED, fg=MUTED)
        model3d_button.config(state=tk.DISABLED, fg=MUTED)
    else:
        jarvis_button.config(bg="#00c8d8", fg="#000000", highlightbackground=BLUE)
        vision_button.config(bg="#031016", fg=MUTED, highlightbackground="#33444c")
        ultron_button.config(bg="#031016", fg=MUTED, highlightbackground="#33444c")
        vision_panel.pack_forget()
        chat_area.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 8))
        refresh_ready_status()
        if channel_label:
            channel_label.config(text="CHANNEL  ·  PRIMARY / LINGUISTIC")
        current_attachment = current_attachment_text = current_attachment_name = None
        if attach_button:
            attach_button.config(state=tk.DISABLED, fg=MUTED)
        if generate_button:
            generate_button.config(state=tk.DISABLED, fg=MUTED)
        if model3d_button:
            model3d_button.config(state=tk.DISABLED, fg=MUTED)


def attach_file():
    global current_attachment, current_attachment_text, current_attachment_name
    if current_mode != "vision":
        messagebox.showinfo("VISION only", "Attachments are available only in VISION mode.")
        return
    path = filedialog.askopenfilename(
        title="Attach file",
        filetypes=[("Supported", "*.png *.jpg *.jpeg *.webp *.txt *.pdf *.csv"), ("All files", "*.*")],
    )
    if not path:
        return
    ext = os.path.splitext(path)[1].lower()
    if ext in (".png", ".jpg", ".jpeg", ".webp"):
        current_attachment, current_attachment_text = path, None
        current_attachment_name = os.path.basename(path)
        show_attachment_status(f"IMAGE READY: {current_attachment_name}")
        return
    if ext == ".txt":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            set_text_attachment(path, f.read())
        return
    if ext == ".pdf":
        if PdfReader is None:
            messagebox.showerror("Missing package", "python -m pip install pypdf")
            return
        text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
        set_text_attachment(path, text)
        return
    if ext == ".csv":
        df = pd.read_csv(path)
        set_text_attachment(path, df.to_string(index=False))
        create_visualization(df)


def set_text_attachment(path, text):
    global current_attachment, current_attachment_text, current_attachment_name
    current_attachment = None
    current_attachment_text, current_attachment_name = text, os.path.basename(path)
    show_attachment_status(f"FILE READY: {current_attachment_name}")


def show_attachment_status(message):
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, f"\n{message}\n", "attachment")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)


def generate_offline_3d_mesh(prompt_text):
    """Render a procedural 3D preview locally when an API is unavailable."""
    plt.style.use("dark_background")
    figure = plt.figure(figsize=(7, 6), facecolor="#050b14")
    axes = figure.add_subplot(111, projection="3d", facecolor="#050b14")
    prompt_lower = prompt_text.lower()

    if any(word in prompt_lower for word in ("sphere", "ball", "planet")):
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 30)
        x = 10 * np.outer(np.cos(u), np.sin(v))
        y = 10 * np.outer(np.sin(u), np.sin(v))
        z = 10 * np.outer(np.ones(np.size(u)), np.cos(v))
        axes.plot_wireframe(x, y, z, color="#00f3ff", linewidth=0.8)
        title_text = "HYPER-SPHERE 3D MESH"
    elif any(word in prompt_lower for word in ("cube", "box", "chest")):
        corners = (-5, 5)
        for y in corners:
            for z in corners:
                axes.plot(corners, (y, y), (z, z), color="#00f3ff", linewidth=2)
        for x in corners:
            for z in corners:
                axes.plot((x, x), corners, (z, z), color="#00f3ff", linewidth=2)
        for x in corners:
            for y in corners:
                axes.plot((x, x), (y, y), corners, color="#00f3ff", linewidth=2)
        title_text = "3D CUBE CONTAINER MATRIX"
    elif any(word in prompt_lower for word in ("car", "vehicle")):
        x = np.linspace(-10, 10, 20)
        y = np.linspace(-4, 4, 10)
        mesh_x, mesh_y = np.meshgrid(x, y)
        mesh_z = np.exp(-(mesh_x ** 2) / 20) * 3 + np.cos(mesh_y)
        axes.plot_wireframe(mesh_x, mesh_y, mesh_z, color="#00ff9d", linewidth=1.2)
        title_text = "CHASSIS / VEHICLE WIREFRAME"
    else:
        x = np.linspace(-8, 8, 40)
        y = np.linspace(-8, 8, 40)
        mesh_x, mesh_y = np.meshgrid(x, y)
        mesh_z = np.sin(np.sqrt(mesh_x ** 2 + mesh_y ** 2)) * 3
        axes.plot_surface(mesh_x, mesh_y, mesh_z, cmap="cool", edgecolor="#00f3ff", alpha=0.7, linewidth=0.2)
        title_text = f"GENERIC 3D MODEL: {prompt_text[:15].upper()}"

    axes.set_title(f"JARVIS HUD 3D CORE // {title_text}", color="#00f3ff", fontsize=10, pad=10)
    axes.grid(False)
    axes.axis("off")
    plt.tight_layout()
    plt.show()


def _generate_offline_3d_worker(prompt):
    try:
        generate_offline_3d_mesh(prompt)
        root.after(0, display_response, f"Offline 3D preview finished for: {prompt}")
    except Exception as error:
        root.after(0, finish_error, error)
    finally:
        root.after(0, stop_thinking)
        root.after(0, lambda: model3d_button and model3d_button.config(state=tk.NORMAL, fg=MAGENTA))


def generate_3d_model(prompt=None):
    """Generate a Meshy model or a local basic shape without an API key."""
    if current_mode != "vision":
        messagebox.showinfo("VISION only", "3D model generation is available only in VISION mode.")
        return
    if prompt is None:
        prompt = simpledialog.askstring(
            "J.A.R.V.I.S. 3D MODEL GENERATOR",
            "Describe the 3D model:\n\nExample: futuristic red-and-gold superhero armor suit, full body, detailed mechanical panels",
            parent=root,
        )
    if not prompt or not prompt.strip():
        return
    prompt = prompt.strip()[:600]
    if is_shape_collection_request(prompt):
        try:
            path, shape = _open_shape_collection_viewer(prompt)
            display_response(f"Local {shape} model created without Meshy, Sir.\nSaved viewer: {path}")
        except Exception as error:
            display_error(f"Local shape collection generation failed: {error}")
        return
    if is_simple_shape_request(prompt):
        try:
            path, shape = _open_simple_shape_viewer(prompt)
            display_response(f"Local {shape} model created without Meshy, Sir.\nSaved viewer: {path}")
        except Exception as error:
            display_error(f"Local shape generation failed: {error}")
        return
    if not MESHY_API_KEY:
        start_thinking()
        if model3d_button:
            model3d_button.config(state=tk.DISABLED, fg=MUTED)
        threading.Thread(target=_generate_offline_3d_worker, args=(prompt,), daemon=True).start()
        return
    start_thinking()
    if model3d_button:
        model3d_button.config(state=tk.DISABLED, fg=MUTED)
    threading.Thread(target=_generate_3d_model_worker, args=(prompt,), daemon=True).start()


def _meshy_headers():
    return {"Authorization": f"Bearer {MESHY_API_KEY}", "Content-Type": "application/json"}


def _meshy_create(mode, prompt=None, preview_task_id=None):
    if mode == "preview":
        payload = {"mode": "preview", "prompt": prompt, "model_type": "standard", "target_formats": ["glb"], "moderation": True}
    else:
        payload = {"mode": "refine", "preview_task_id": preview_task_id, "enable_pbr": True, "texture_resolution": "2k", "target_formats": ["glb"], "moderation": True}
    r = requests.post(MESHY_BASE_URL, headers=_meshy_headers(), json=payload, timeout=60)
    if not r.ok:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        if r.status_code in (401, 403):
            raise RuntimeError(
                "Meshy rejected the API key. Create or copy a valid key from your Meshy account, "
                "set the Windows MESHY_API_KEY environment variable, then restart JARVIS."
            )
        raise RuntimeError(f"Meshy {mode} request failed ({r.status_code}): {detail}")
    body = r.json()
    task_id = body.get("result") or body.get("id") or body.get("task_id")
    if isinstance(task_id, dict):
        task_id = task_id.get("id") or task_id.get("task_id") or task_id.get("result")
    if not task_id:
        raise RuntimeError(f"Meshy did not return a task ID: {body}")
    return task_id


def _meshy_wait(task_id, label):
    url = f"{MESHY_BASE_URL}/{task_id}"
    while True:
        r = requests.get(url, headers=_meshy_headers(), timeout=60)
        if not r.ok:
            raise RuntimeError(f"Meshy status request failed ({r.status_code}): {r.text}")
        task = r.json()
        status = str(task.get("status", "")).upper()
        progress = int(task.get("progress") or 0)
        root.after(0, set_listening_status, f"3D {label}  •  {progress}%")
        if status in ("SUCCEEDED", "SUCCESS", "COMPLETED"):
            return task
        if status in ("FAILED", "ERROR", "CANCELED", "CANCELLED"):
            terr = task.get("task_error") or task.get("error") or {}
            error = terr.get("message") if isinstance(terr, dict) else str(terr)
            error = error or "Unknown generation error"
            raise RuntimeError(f"3D generation failed: {error}")
        time.sleep(5)


def _download_binary(url, path):
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    with open(path, "wb") as f:
        f.write(r.content)


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _open_simple_shape_viewer(prompt):
    global active_3d_close_path, active_3d_close_token
    prompt_lower = prompt.lower()
    shape_match = re.search(r"\b(circle|disc|disk|square|rectangle|triangle|cube|sphere|cylinder|cone|torus|pyramid|capsule|octahedron|icosahedron|dodecahedron|tetrahedron|knot)\b", prompt_lower)
    shape = shape_match.group(1) if shape_match else "cube"
    if shape in {"disc", "disk"}:
        shape = "circle"
    colors = {"red": "#ff4264", "green": "#39ff88", "blue": "#4da6ff", "gold": "#ffd166", "orange": "#ff9f43", "white": "#e8f6f8", "pink": "#ff5fd2", "cyan": "#00d8cc"}
    color = next((value for name, value in colors.items() if re.search(rf"\b{name}\b", prompt_lower)), "#00d8cc")
    size_match = re.search(r"\b(?:size|scale)\s*(?:of|is|=)?\s*(\d+(?:\.\d+)?)", prompt_lower)
    size = max(0.25, min(4.0, float(size_match.group(1)))) if size_match else 1.0
    detail_match = re.search(r"\b(?:detail|segments|resolution)\s*(?:of|is|=)?\s*(\d+)", prompt_lower)
    detail = max(8, min(96, int(detail_match.group(1)))) if detail_match else 32
    folder = os.path.join(BASE_DIR, "jarvis_3d_models")
    os.makedirs(folder, exist_ok=True)
    active_3d_close_path = os.path.join(folder, "active_3d_close.flag")
    active_3d_close_token = time.strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
    with open(active_3d_close_path, "w", encoding="utf-8") as close_file:
        close_file.write(active_3d_close_token)
    filename = "simple_" + shape + "_" + time.strftime("%Y%m%d_%H%M%S") + ".html"
    path = os.path.join(folder, filename)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JARVIS 3D // {shape.upper()}</title><script type="importmap">{{"imports":{{"three":"https://unpkg.com/three@0.170.0/build/three.module.js","three/addons/":"https://unpkg.com/three@0.170.0/examples/jsm/"}}}}</script>
<style>html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#02060a;color:#dffcff;font-family:Consolas,monospace}}header{{height:54px;display:flex;align-items:center;padding:0 18px;box-sizing:border-box;border-bottom:1px solid #00a8b8;background:#050a0f;gap:14px}}.title{{color:#00ffff;font-weight:bold;letter-spacing:2px}}.hint{{margin-left:auto;color:#6b858d;font-size:12px}}button,input{{accent-color:#00d8cc}}button{{background:#06222a;color:#dffcff;border:1px solid #00a8b8;padding:6px 9px;font-family:Consolas,monospace;cursor:pointer}}canvas{{display:block}}</style></head>
<body><header><div class="title">J.A.R.V.I.S.1 // LOCAL GEOMETRY CORE</div><div class="hint">{shape.upper()} · DRAG TO ROTATE · SCROLL TO ZOOM</div><label>SIZE <input id="size" type="range" min=".25" max="4" step=".05" value="{size}"></label><button id="obj">EXPORT OBJ</button><button id="stl">EXPORT STL</button></header><script type="module">
import * as THREE from 'three'; import {{OrbitControls}} from 'three/addons/controls/OrbitControls.js'; import {{OBJExporter}} from 'three/addons/exporters/OBJExporter.js'; import {{STLExporter}} from 'three/addons/exporters/STLExporter.js';
const scene=new THREE.Scene(); scene.background=new THREE.Color(0x02060a); const camera=new THREE.PerspectiveCamera(45,innerWidth/(innerHeight-54),.1,100); camera.position.set(3,2.4,4.5);
const renderer=new THREE.WebGLRenderer({{antialias:true}}); renderer.setPixelRatio(devicePixelRatio); renderer.setSize(innerWidth,innerHeight-54); document.body.appendChild(renderer.domElement); scene.add(new THREE.HemisphereLight(0x9defff,0x081018,2.2)); const light=new THREE.DirectionalLight(0x00ffff,3); light.position.set(3,4,5); scene.add(light);
let geometry; const detail={detail}; if('{shape}'==='circle') geometry=new THREE.CylinderGeometry(1.35,1.35,.35,detail); else if('{shape}'==='square') geometry=new THREE.BoxGeometry(2.2,.45,2.2); else if('{shape}'==='rectangle') geometry=new THREE.BoxGeometry(3.2,.45,1.7); else if('{shape}'==='triangle') {{const s=new THREE.Shape();s.moveTo(0,1.3);s.lineTo(-1.3,-1);s.lineTo(1.3,-1);s.closePath();geometry=new THREE.ExtrudeGeometry(s,{{depth:.5,bevelEnabled:true,bevelSize:.08,bevelThickness:.08}});geometry.center();}} else if('{shape}'==='sphere') geometry=new THREE.SphereGeometry(1.25,detail,Math.max(8,Math.floor(detail*.67))); else if('{shape}'==='cylinder') geometry=new THREE.CylinderGeometry(.95,.95,2.2,detail); else if('{shape}'==='cone') geometry=new THREE.ConeGeometry(1.2,2.2,detail); else if('{shape}'==='torus') geometry=new THREE.TorusGeometry(1.1,.35,Math.max(8,Math.floor(detail/2)),detail); else if('{shape}'==='pyramid' || '{shape}'==='tetrahedron') geometry=new THREE.ConeGeometry(1.35,2.2,4); else if('{shape}'==='capsule') geometry=new THREE.CapsuleGeometry(.8,1.2,Math.max(4,Math.floor(detail/4)),detail); else if('{shape}'==='octahedron') geometry=new THREE.OctahedronGeometry(1.45); else if('{shape}'==='icosahedron') geometry=new THREE.IcosahedronGeometry(1.45,Math.min(3,Math.floor(detail/16))); else if('{shape}'==='dodecahedron') geometry=new THREE.DodecahedronGeometry(1.45,Math.min(2,Math.floor(detail/24))); else if('{shape}'==='knot') geometry=new THREE.TorusKnotGeometry(1.05,.32,detail,Math.max(4,Math.floor(detail/4))); else geometry=new THREE.BoxGeometry(2,2,2);
const object=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({{color:'{color}',metalness:.65,roughness:.24}})); scene.add(object); const grid=new THREE.GridHelper(8,16,0x09505b,0x08252d); grid.position.y=-1.35; scene.add(grid); const controls=new OrbitControls(camera,renderer.domElement); controls.enableDamping=true; document.getElementById('size').oninput=e=>object.scale.setScalar(Number(e.target.value));
function download(data,name,type){{const blob=new Blob([data],{{type}});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=name;link.click();URL.revokeObjectURL(link.href)}} document.getElementById('obj').onclick=()=>download(new OBJExporter().parse(object),'jarvis_{shape}.obj','text/plain'); document.getElementById('stl').onclick=()=>download(new STLExporter().parse(object),'jarvis_{shape}.stl','model/stl');
const closeToken='{active_3d_close_token}'; setInterval(()=>fetch('active_3d_close.flag?x='+Date.now()).then(response=>response.text()).then(value=>{{if(value.trim()==='CLOSE' && closeToken) location.replace('about:blank')}}).catch(()=>{{}}),1000);
function animate(){{requestAnimationFrame(animate);object.rotation.y+=.005;controls.update();renderer.render(scene,camera)}} animate(); addEventListener('resize',()=>{{camera.aspect=innerWidth/(innerHeight-54);camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight-54)}});
</script></body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    port = _find_free_port()
    import http.server
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
    def handler_factory(*args, **kwargs):
        return QuietHandler(*args, directory=folder, **kwargs)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler_factory)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}/{urllib.parse.quote(filename)}")
    return path, shape


def _open_shape_collection_viewer(prompt):
    global active_3d_close_path, active_3d_close_token
    prompt_lower = (prompt or "").lower()
    default_shapes = ["cube", "sphere", "cylinder", "cone", "torus", "pyramid"]
    shape_names = [name for name in default_shapes if re.search(rf"\b{name}\b", prompt_lower)]
    if not shape_names:
        shape_names = default_shapes

    colors = {
        "red": "#ff4264",
        "green": "#39ff88",
        "blue": "#4da6ff",
        "gold": "#ffd166",
        "orange": "#ff9f43",
        "white": "#e8f6f8",
        "pink": "#ff5fd2",
        "cyan": "#00d8cc",
    }
    size_match = re.search(r"\b(?:size|scale)\s*(?:of|is|=)?\s*(\d+(?:\.\d+)?)", prompt_lower)
    size = max(0.45, min(2.2, float(size_match.group(1)))) if size_match else 1.0

    folder = os.path.join(BASE_DIR, "jarvis_3d_models")
    os.makedirs(folder, exist_ok=True)
    active_3d_close_path = os.path.join(folder, "active_3d_close.flag")
    active_3d_close_token = time.strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
    with open(active_3d_close_path, "w", encoding="utf-8") as close_file:
        close_file.write(active_3d_close_token)

    filename = "shapes_" + time.strftime("%Y%m%d_%H%M%S") + ".html"
    path = os.path.join(folder, filename)

    specs = []
    palette = ["#00d8cc", "#ff5fd2", "#ffd166", "#39ff88", "#4da6ff", "#ff9f43"]
    for index, shape in enumerate(shape_names[:6]):
        color = next(
            (value for name, value in colors.items() if re.search(rf"\b{name}\b", prompt_lower)),
            palette[index % len(palette)],
        )
        specs.append({
            "name": shape,
            "color": color,
            "x": -2.5 + (index % 3) * 2.5,
            "y": 0.25 if index < 3 else -0.5,
            "z": -1.0 + (index // 3) * 2.0,
            "scale": max(0.55, min(1.5, size)),
        })

    specs_json = json.dumps(specs)
    html = f"""<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JARVIS 3D // SHAPES</title><script type="importmap">{{"imports":{{"three":"https://unpkg.com/three@0.170.0/build/three.module.js","three/addons/":"https://unpkg.com/three@0.170.0/examples/jsm/"}}}}</script>
<style>html,body{{margin:0;width:100%;height:100%;overflow:hidden;background:#02060a;color:#dffcff;font-family:Consolas,monospace}}header{{height:54px;display:flex;align-items:center;padding:0 18px;box-sizing:border-box;border-bottom:1px solid #00a8b8;background:#050a0f;gap:14px}}.title{{color:#00ffff;font-weight:bold;letter-spacing:2px}}.hint{{margin-left:auto;color:#6b858d;font-size:12px}}button,input{{accent-color:#00d8cc}}button{{background:#06222a;color:#dffcff;border:1px solid #00a8b8;padding:6px 9px;font-family:Consolas,monospace;cursor:pointer}}canvas{{display:block}}</style></head>
<body><header><div class="title">J.A.R.V.I.S. // LOCAL GEOMETRY CORE</div><div class="hint">SHAPES · DRAG TO ROTATE · SCROLL TO ZOOM</div><label>SIZE <input id="size" type="range" min=".35" max="2.2" step=".05" value="{size}"></label><button id="obj">EXPORT OBJ</button><button id="stl">EXPORT STL</button></header><script type="module">
import * as THREE from 'three';
import {{OrbitControls}} from 'three/addons/controls/OrbitControls.js';
import {{OBJExporter}} from 'three/addons/exporters/OBJExporter.js';
import {{STLExporter}} from 'three/addons/exporters/STLExporter.js';

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x02060a);
const camera = new THREE.PerspectiveCamera(42, innerWidth / (innerHeight - 54), .1, 100);
camera.position.set(6.5, 4.5, 7.8);

const renderer = new THREE.WebGLRenderer({{antialias: true}});
renderer.setPixelRatio(devicePixelRatio);
renderer.setSize(innerWidth, innerHeight - 54);
document.body.appendChild(renderer.domElement);

scene.add(new THREE.HemisphereLight(0x9defff, 0x081018, 2.3));
const dir = new THREE.DirectionalLight(0x00ffff, 3);
dir.position.set(4, 6, 5);
scene.add(dir);

const group = new THREE.Group();
scene.add(group);

const geometryMap = {{
  cube: new THREE.BoxGeometry(1.2, 1.2, 1.2),
  sphere: new THREE.SphereGeometry(0.78, 32, 20),
  cylinder: new THREE.CylinderGeometry(0.62, 0.62, 1.7, 32),
  cone: new THREE.ConeGeometry(0.8, 1.7, 32),
  torus: new THREE.TorusGeometry(0.78, 0.24, 16, 48),
  pyramid: new THREE.ConeGeometry(0.92, 1.7, 4)
}};

const specs = {specs_json};
const meshes = [];
for (const spec of specs) {{
  const mesh = new THREE.Mesh(
    geometryMap[spec.name] || geometryMap.cube,
    new THREE.MeshStandardMaterial({{color: spec.color, metalness: 0.6, roughness: 0.28}})
  );
  mesh.position.set(spec.x, spec.y, spec.z);
  mesh.rotation.set(Math.random() * 1.2, Math.random() * 1.4, Math.random() * 1.1);
  mesh.scale.setScalar(spec.scale);
  group.add(mesh);
  meshes.push(mesh);
}}

const grid = new THREE.GridHelper(10, 16, 0x09505b, 0x08252d);
grid.position.y = -1.2;
scene.add(grid);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;

const sizeSlider = document.getElementById('size');
sizeSlider.oninput = (event) => {{
  const value = Number(event.target.value);
  for (const mesh of meshes) mesh.scale.setScalar(value);
}};

function download(data, name, type) {{
  const blob = new Blob([data], {{type}});
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = name;
  link.click();
  URL.revokeObjectURL(link.href);
}}

document.getElementById('obj').onclick = () => download(new OBJExporter().parse(group), 'jarvis_shapes.obj', 'text/plain');
document.getElementById('stl').onclick = () => download(new STLExporter().parse(group), 'jarvis_shapes.stl', 'model/stl');

const closeToken = '{active_3d_close_token}';
setInterval(() => fetch('active_3d_close.flag?x=' + Date.now())
  .then((response) => response.text())
  .then((value) => {{ if (value.trim() === 'CLOSE' && closeToken) location.replace('about:blank'); }})
  .catch(() => {{}}), 1000);

function animate() {{
  requestAnimationFrame(animate);
  group.rotation.y += 0.005;
  controls.update();
  renderer.render(scene, camera);
}}
animate();
addEventListener('resize', () => {{
  camera.aspect = innerWidth / (innerHeight - 54);
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight - 54);
}});
</script></body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    port = _find_free_port()
    import http.server
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
    def handler_factory(*args, **kwargs):
        return QuietHandler(*args, directory=folder, **kwargs)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler_factory)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}/{urllib.parse.quote(filename)}")
    return path, "shapes"


def _open_3d_viewer(model_path, title):
    """Open the GLB in an interactive browser viewer with rotate/zoom controls."""
    global active_3d_close_path, active_3d_close_token
    import http.server
    folder = os.path.dirname(model_path)
    filename = os.path.basename(model_path)
    active_3d_close_path = os.path.join(folder, "active_3d_close.flag")
    active_3d_close_token = time.strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
    with open(active_3d_close_path, "w", encoding="utf-8") as close_file:
        close_file.write(active_3d_close_token)
    html_path = os.path.join(folder, "viewer.html")
    safe_title = (title or "3D MODEL").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JARVIS 3D // %s</title>
<script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js"></script>
<style>
html,body{margin:0;width:100%%;height:100%%;background:#02060a;color:#dffcff;font-family:Consolas,monospace;overflow:hidden}
header{height:54px;display:flex;align-items:center;padding:0 18px;border-bottom:1px solid #00a8b8;background:#050a0f;box-sizing:border-box}
.title{color:#00ffff;font-weight:bold;letter-spacing:2px}.prompt{margin-left:auto;color:#6b858d;font-size:12px}
model-viewer{width:100%%;height:calc(100%% - 54px);background:#02060a;--poster-color:#02060a}
</style></head><body>
<header><div class="title">J.A.R.V.I.S. // 3D MODEL VIEWER</div><div class="prompt">%s · DRAG TO ROTATE · SCROLL TO ZOOM</div></header>
<model-viewer src="%s" camera-controls auto-rotate shadow-intensity="1" exposure="1.05" environment-image="neutral" alt="%s"></model-viewer>
<script>const closeToken="%s";setInterval(()=>fetch("active_3d_close.flag?x="+Date.now()).then(response=>response.text()).then(value=>{if(value.trim()==="CLOSE"&&closeToken)location.replace("about:blank")}).catch(()=>{}),1000)</script>
</body></html>""" % (safe_title, safe_title, urllib.parse.quote(filename), safe_title, active_3d_close_token)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    port = _find_free_port()
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, format, *args):
            pass
    def handler_factory(*args, **kwargs):
        return QuietHandler(*args, directory=folder, **kwargs)
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler_factory)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    webbrowser.open(f"http://127.0.0.1:{port}/viewer.html")


def _show_3d_result(path, prompt):
    stop_thinking()
    if model3d_button:
        model3d_button.config(state=tk.NORMAL, fg=MAGENTA)
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, "\nJARVIS 3D MODEL GENERATOR\n", "jarvis_label")
    chat_area.insert(tk.END, f"Prompt: {prompt}\nSaved: {path}\nInteractive viewer opened in your browser.\n\n", "jarvis_text")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)
    _open_3d_viewer(path, "3D MODEL")


def _generate_3d_model_worker(prompt):
    try:
        preview_id = _meshy_create("preview", prompt=prompt)
        preview = _meshy_wait(preview_id, "PREVIEW")
        refine_id = _meshy_create("refine", preview_task_id=preview["id"])
        refined = _meshy_wait(refine_id, "TEXTURE")
        model_urls = refined.get("model_urls") or refined.get("modelUrls") or {}
        model_url = model_urls.get("glb") or model_urls.get("GLB")
        if not model_url:
            # Some API responses expose the URL under a top-level field.
            model_url = refined.get("glb_url") or refined.get("glbUrl")
        if not model_url:
            raise RuntimeError(f"Meshy finished but did not return a GLB download URL. Response: {refined}")
        folder = os.path.join(BASE_DIR, "jarvis_3d_models")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "jarvis_3d_" + time.strftime("%Y%m%d_%H%M%S") + ".glb")
        _download_binary(model_url, path)
        root.after(0, _show_3d_result, path, prompt)
    except Exception as e:
        root.after(0, finish_error, e)
        root.after(0, lambda: model3d_button and model3d_button.config(state=tk.NORMAL, fg=MAGENTA))


def generate_image(prompt=None):
    if current_mode != "vision":
        messagebox.showinfo("VISION only", "Image generation is available only in VISION mode.")
        return
    if prompt is None:
        prompt = simpledialog.askstring("J.A.R.V.I.S. Image Generator", "Describe the image:", parent=root)
    if not prompt or not prompt.strip():
        return
    start_thinking()
    threading.Thread(target=_generate_image_worker, args=(prompt.strip(),), daemon=True).start()


def _generate_image_worker(prompt):
    try:
        enhanced_prompt = (
            "High quality detailed digital artwork. "
            "Preserve the user's subject and intent exactly. "
            "Strong composition, realistic lighting, sharp details, clean anatomy, "
            "professional rendering, coherent materials and textures. " + prompt.strip()
        )
        url = "https://image.pollinations.ai/prompt/" + urllib.parse.quote(enhanced_prompt, safe="") + "?width=1280&height=1024&nologo=true&model=flux"
        response = requests.get(url, timeout=90)
        response.raise_for_status()
        folder = os.path.join(BASE_DIR, "jarvis_generated")
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, "jarvis_" + time.strftime("%Y%m%d_%H%M%S") + ".png")
        with open(path, "wb") as f:
            f.write(response.content)
        img = Image.open(io.BytesIO(response.content)).convert("RGB")
        img.thumbnail((700, 500))
        root.after(0, _show_generated_image, img, path, prompt)
    except Exception as e:
        root.after(0, finish_error, e)


def _show_generated_image(img, path, prompt):
    global generated_image_ref
    stop_thinking()
    switch_mode("jarvis")
    generated_image_ref = ImageTk.PhotoImage(img)
    chat_area.config(state=tk.NORMAL)
    chat_area.insert(tk.END, "\nJARVIS IMAGE GENERATOR\n", "jarvis_label")
    chat_area.insert(tk.END, f"Prompt: {prompt}\nSaved: {path}\n", "jarvis_text")
    chat_area.image_create(tk.END, image=generated_image_ref)
    chat_area.insert(tk.END, "\n\n")
    chat_area.config(state=tk.DISABLED)
    chat_area.see(tk.END)


def create_visualization(df):
    numeric = df.select_dtypes(include="number").columns.tolist()
    if not numeric:
        return
    plt.figure(figsize=(8, 5))
    df[numeric[0]].plot(kind="line", marker="o")
    plt.title(f"VISION DATA ANALYSIS — {numeric[0]}")
    plt.tight_layout()
    plt.show()


def location_context_text():
    city = location_info.get("city") or "Unknown"
    region = location_info.get("region") or ""
    country = location_info.get("country") or ""
    lat, lon = location_info.get("latitude"), location_info.get("longitude")
    local_time = time.strftime("%Y-%m-%d %H:%M")
    if ZoneInfo and location_info.get("timezone"):
        try:
            local_time = datetime.now(ZoneInfo(location_info["timezone"])).strftime("%Y-%m-%d %H:%M")
        except Exception:
            pass
    place = ", ".join(p for p in (city, region, country) if p)
    coords = f"{lat:.4f}, {lon:.4f}" if lat is not None and lon is not None else "unknown"
    return (
        "\n\nLOCATION CONTEXT:\n"
        f"- Place: {place}\n- Coordinates: {coords}\n- Timezone: {location_info.get('timezone') or 'local'}\n"
        f"- Local time: {local_time}\n- Weather: {location_info.get('weather_summary') or 'unknown'}\n"
        f"- Source: {location_info.get('source') or 'unknown'}\n"
    )


def apply_location_to_prompts():
    addon = location_context_text() + memory_context()
    if jarvis_messages:
        jarvis_messages[0] = {"role": "system", "content": SYSTEM_PROMPT + addon}
    if vision_messages:
        vision_messages[0] = {"role": "system", "content": SYSTEM_PROMPT + addon}


def save_location():
    try:
        keys = ("city", "region", "country", "latitude", "longitude", "timezone", "ip", "source")
        with open(LOCATION_PATH, "w", encoding="utf-8") as f:
            json.dump({k: location_info.get(k) for k in keys}, f, indent=2)
    except Exception:
        pass


def load_saved_location():
    try:
        with open(LOCATION_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if data.get("latitude") is None:
            return False
        location_info.update(data)
        return True
    except Exception:
        return False


def fetch_weather(lat, lon, timezone="auto"):
    data = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": timezone or "auto", "forecast_days": 2,
        },
        timeout=10,
    ).json()
    current, daily = data.get("current", {}), data.get("daily", {})
    condition = WMO_TEXT.get(current.get("weather_code"), "Conditions unknown")
    tmax = (daily.get("temperature_2m_max") or ["?"])[0]
    tmin = (daily.get("temperature_2m_min") or ["?"])[0]
    weather_text = (
        f"{current.get('temperature_2m', '?')}°C  ·  {condition}\n"
        f"Feels {current.get('apparent_temperature', '?')}°C\n"
        f"Humidity {current.get('relative_humidity_2m', '?')}%\n"
        f"Wind {current.get('wind_speed_10m', '?')} km/h\n"
        f"Today  {tmin}° / {tmax}°"
    )
    weather_summary = (
        f"{condition}, {current.get('temperature_2m', '?')}°C "
        f"(feels {current.get('apparent_temperature', '?')}°C), "
        f"humidity {current.get('relative_humidity_2m', '?')}%"
    )
    return weather_text, weather_summary, data.get("timezone") or timezone or ""


def detect_ip_location():
    d = requests.get(
        "http://ip-api.com/json/?fields=status,country,regionName,city,lat,lon,timezone,query",
        timeout=8,
    ).json()
    if d.get("status") == "success" and d.get("lat") is not None:
        return {
            "city": d.get("city") or "Unknown", "region": d.get("regionName") or "",
            "country": d.get("country") or "", "latitude": d.get("lat"), "longitude": d.get("lon"),
            "timezone": d.get("timezone") or "", "ip": d.get("query") or "",
            "source": "IP geolocation (ip-api)",
        }
    raise RuntimeError("Could not detect location")


def geocode_city(query):
    results = (
        requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": query, "count": 1, "language": "en", "format": "json"}, timeout=10,
        ).json().get("results") or []
    )
    if not results:
        raise RuntimeError(f"No match for '{query}'.")
    hit = results[0]
    return {
        "city": hit.get("name") or query, "region": hit.get("admin1") or "",
        "country": hit.get("country") or "", "latitude": hit.get("latitude"),
        "longitude": hit.get("longitude"), "timezone": hit.get("timezone") or "",
        "ip": location_info.get("ip") or "", "source": "User-set city",
    }


def push_location_ui():
    place = ", ".join(p for p in (location_info.get("city"), location_info.get("region"), location_info.get("country")) if p)
    lat, lon = location_info.get("latitude"), location_info.get("longitude")
    coords = f"{lat:.3f}, {lon:.3f}" if lat is not None and lon is not None else "—"
    if location_value:
        location_value.config(text=f"{place}\n{coords}\n{location_info.get('source') or ''}")
    if weather_value:
        weather_value.config(text=location_info.get("weather_text") or "Unavailable")
    if location_status:
        location_status.config(text=f"LOC  ·  {location_info.get('city') or 'UNKNOWN'}")


def get_location_and_weather(force_detect=True):
    try:
        if force_detect:
            location_info.update(detect_ip_location())
            save_location()
        lat, lon = location_info.get("latitude"), location_info.get("longitude")
        if lat is None:
            raise RuntimeError("No coordinates")
        weather_text, weather_summary, tz = fetch_weather(lat, lon, location_info.get("timezone") or "auto")
        location_info["weather_text"] = weather_text
        location_info["weather_summary"] = weather_summary
        if tz:
            location_info["timezone"] = tz
        apply_location_to_prompts()
        if root:
            root.after(0, push_location_ui)
    except Exception as e:
        if root and weather_value:
            root.after(0, lambda: weather_value.config(text=f"Unavailable\n{e}"))


def refresh_location():
    if location_status:
        location_status.config(text="LOC  ·  SCANNING")
    threading.Thread(target=get_location_and_weather, kwargs={"force_detect": True}, daemon=True).start()


def set_location_manual():
    query = simpledialog.askstring("Set location", "City name:", parent=root)
    if not query or not query.strip():
        return

    def worker():
        try:
            loc = geocode_city(query.strip())
            location_info.update(loc)
            weather_text, weather_summary, tz = fetch_weather(loc["latitude"], loc["longitude"], loc.get("timezone") or "auto")
            location_info["weather_text"] = weather_text
            location_info["weather_summary"] = weather_summary
            if tz:
                location_info["timezone"] = tz
            save_location()
            apply_location_to_prompts()
            if root:
                root.after(0, push_location_ui)
        except Exception as e:
            if root:
                root.after(0, lambda: messagebox.showerror("Location", str(e)))
    threading.Thread(target=worker, daemon=True).start()


def draw_globe():
    global globe_angle, scan_lat, scan_dir, w_phase
    if globe_canvas is None or root is None:
        return
    try:
        globe_canvas.delete("globe")
        w = max(globe_canvas.winfo_width(), 300)
        h = max(globe_canvas.winfo_height(), 280)
        cx, cy = w / 2, h / 2 - 8
        radius = min(w, h) * 0.34
        now = time.time()
        ensure_starfield()

        for sx, sy, bright in globe_stars:
            px, py = sx * w, sy * h
            twinkle = 0.55 + 0.45 * math.sin(now * (1.2 + bright * 3.0) + bright * 12)
            shade = 40 + 180 * bright * twinkle
            size = 1.1 + bright * 1.4
            globe_canvas.create_oval(
                px - size, py - size, px + size, py + size,
                fill=hex_color(shade * 0.45, shade * 0.85, shade), outline="", tags="globe",
            )

        for i, factor in enumerate((1.52, 1.38, 1.24)):
            r = radius * factor
            pulse = 1 + (i == 1) * (0.5 + 0.5 * math.sin(now * 2.4))
            globe_canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#72500a" if i else "#d89b16", width=pulse, tags="globe")

        for glow, color in ((1.12, "#302006"), (1.06, "#563807")):
            r = radius * glow
            globe_canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline="", tags="globe")

        core = radius * 0.25
        globe_canvas.create_oval(cx - core, cy - core, cx + core, cy + core, fill="#241905", outline=GOLD, width=1, tags="globe")
        globe_canvas.create_oval(cx - core * 0.45, cy - core * 0.45, cx + core * 0.45, cy + core * 0.45, fill=GOLD, outline="", tags="globe")
        for core_ring, core_width in ((0.62, 1), (0.82, 1), (1.08, 2)):
            ring = core * core_ring
            globe_canvas.create_oval(cx - ring, cy - ring, cx + ring, cy + ring, outline="#f0b52b", width=core_width, tags="globe")

        for a, b in TESSERACT_EDGES:
            p1 = project_tesseract_vertex(*a, radius, cx, cy)
            p2 = project_tesseract_vertex(*b, radius, cx, cy)
            midz = (p1[2] + p2[2]) / 2
            col = "#ffcf3a" if midz >= 0 else "#6b4807"
            globe_canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=col, width=2 if midz >= 0 else 1, tags="globe")

        faces = []
        lat_step, lon_step = 15, 18
        for lat in range(-90, 90, lat_step):
            for lon in range(-180, 180, lon_step):
                corners = [
                    latlon_to_xyz(lat, lon, globe_angle, radius),
                    latlon_to_xyz(lat, lon + lon_step, globe_angle, radius),
                    latlon_to_xyz(lat + lat_step, lon + lon_step, globe_angle, radius),
                    latlon_to_xyz(lat + lat_step, lon, globe_angle, radius),
                ]
                mx = sum(p[0] for p in corners) / 4
                my = sum(p[1] for p in corners) / 4
                mz = sum(p[2] for p in corners) / 4
                if mz < -radius * 0.02:
                    continue
                pts = []
                for x, y, z in corners:
                    px, py, _, _ = project_xyz(x, y, z, cx, cy, radius)
                    pts += [px, py]
                mid_lat = lat + lat_step / 2
                faces.append((mz, pts, face_fill(mx, my, mz, radius, mid_lat, scan_lat), mid_lat))
        faces.sort(key=lambda item: item[0])
        for mz, pts, fill, mid_lat in faces:
            outline = "#ffe06a" if abs(mid_lat - scan_lat) < 8 else "#8f610b"
            globe_canvas.create_polygon(*pts, fill=fill, outline=outline, width=1, stipple="gray25", tags="globe")

        for lat in range(-75, 76, 10):
            points = []
            for lon in range(-180, 181, 6):
                px, py, pz, *_ = project_latlon(lat, lon, globe_angle, radius, cx, cy)
                if pz >= 0:
                    points += [px, py]
                elif len(points) >= 4:
                    draw_polyline(points, "#d99a16", 1)
                    points = []
            if len(points) >= 4:
                draw_polyline(points, "#d99a16", 1)

        for band, width, color in ((0, 2, "#ffe06a"), (23.5, 1, "#e5ab22"), (-23.5, 1, "#e5ab22")):
            points = []
            for lon in range(-180, 181, 4):
                px, py, pz, *_ = project_latlon(band, lon, globe_angle, radius, cx, cy)
                if pz >= 0:
                    points += [px, py]
                elif len(points) >= 4:
                    draw_polyline(points, color, width)
                    points = []
            if len(points) >= 4:
                draw_polyline(points, color, width)

        ghost = w_phase + 0.9
        for lon in range(-180, 181, 18):
            points = []
            for lat in range(-90, 91, 5):
                px, py, pz, *_ = project_latlon(lat, lon, globe_angle, radius * 0.92, cx, cy, phase=ghost)
                if pz >= 0:
                    points += [px, py]
                elif len(points) >= 4:
                    draw_polyline(points, "#f0b52b", 1)
                    points = []
            if len(points) >= 4:
                draw_polyline(points, "#f0b52b", 1)

        ox = 3.5 * math.sin(now * 2.2)
        globe_canvas.create_oval(cx - radius + ox, cy - radius, cx + radius + ox, cy + radius, outline="#f0b52b", width=1, tags="globe")
        globe_canvas.create_oval(cx - radius - ox, cy - radius, cx + radius - ox, cy + radius, outline="#ffe06a", width=2, tags="globe")

        draw_orbit_ring(cx, cy, radius, 78, globe_angle * 0.4, "#ffd34d", 2, 1.26)
        draw_orbit_ring(cx, cy, radius, 62, -globe_angle * 0.55 + 40, "#e5ab22", 1, 1.31)
        draw_orbit_ring(cx, cy, radius, 42, globe_angle * 0.32 - 25, "#c88712", 1, 1.22)
        draw_orbit_ring(cx, cy, radius, 88, -globe_angle * 0.24, "#f0b52b", 1, 1.38)

        lat = location_info.get("latitude")
        lon = location_info.get("longitude")
        if lat is not None and lon is not None:
            for city in NETWORK_CITIES:
                draw_great_arc(float(lat), float(lon), city[0], city[1], globe_angle, radius, cx, cy)
            px, py, pz, scale, *_ = project_latlon(float(lat), float(lon), globe_angle, radius, cx, cy)
            if pz >= -radius * 0.05:
                pulse = (7 + 4 * math.sin(now * 5)) * scale
                globe_canvas.create_oval(px - pulse, py - pulse, px + pulse, py + pulse, outline=GREEN, width=2, tags="globe")
                globe_canvas.create_oval(px - 4 * scale, py - 4 * scale, px + 4 * scale, py + 4 * scale, fill=GREEN, outline="", tags="globe")

        globe_canvas.create_text(cx, h - 28, text="J.A.R.V.I.S.  4D GLOBAL CORE  •  HYPERSPHERE", fill=GOLD, font=(FONT, 8, "bold"), tags="globe")
        globe_canvas.create_text(cx, h - 14, text=f"W-PHASE {w_phase:.2f}  •  TESSERACT LOCK", fill="#e5ab22", font=(FONT, 7), tags="globe")

        globe_angle = (globe_angle + 0.7) % 360
        w_phase = (w_phase + 0.017) % (math.pi * 2)
        scan_lat += scan_dir * 0.85
        if scan_lat > 78:
            scan_lat, scan_dir = 78, -1.0
        elif scan_lat < -78:
            scan_lat, scan_dir = -78, 1.0
        root.after(33, draw_globe)
    except Exception:
        root.after(100, draw_globe)


def draw_neural_meters():
    if neural_canvas is None or wave_canvas is None:
        return
    now = time.time()
    neural_canvas.delete("all")
    wave_canvas.delete("all")
    w = 168
    load = 0.28 + 0.18 * math.sin(now * 1.3) + (0.45 if thinking_running else 0)
    load = max(0.08, min(0.97, load))
    neural_canvas.create_rectangle(0, 8, w, 20, fill="#061015", outline="#123846")
    neural_canvas.create_rectangle(0, 8, w * load, 20, fill=BLUE if not thinking_running else MAGENTA, outline="")
    neural_canvas.create_text(2, 4, text="NEURAL LOAD", fill=MUTED, font=(FONT, 6), anchor="w")
    ww = max(wave_canvas.winfo_width(), 180)
    wh = max(wave_canvas.winfo_height(), 36)
    mid = wh / 2
    pts = []
    amp = 10 if thinking_running else 4
    for x in range(0, ww, 3):
        y = mid + amp * math.sin(x * 0.09 + now * 6) + (amp * 0.4) * math.sin(x * 0.21 + now * 9)
        pts += [x, y]
    if len(pts) >= 4:
        wave_canvas.create_line(*pts, fill=GREEN if thinking_running else BLUE, width=1, smooth=True)
    wave_canvas.create_line(0, mid, ww, mid, fill="#123846")


def tick_hud():
    if root is None:
        return
    try:
        if clock_label:
            tz_name = location_info.get("timezone")
            if ZoneInfo and tz_name:
                try:
                    clock_label.config(text=datetime.now(ZoneInfo(tz_name)).strftime("%H:%M:%S"))
                except Exception:
                    clock_label.config(text=time.strftime("%H:%M:%S"))
            else:
                clock_label.config(text=time.strftime("%H:%M:%S"))
        if uptime_label:
            elapsed = int(time.time() - session_started)
            h, rem = divmod(elapsed, 3600)
            m, s = divmod(rem, 60)
            uptime_label.config(text=f"UP {h:02d}:{m:02d}:{s:02d}")
        if wphase_label:
            wphase_label.config(text=f"W {w_phase:.2f}")
        draw_wake_signal()
        draw_neural_meters()
    except Exception:
        pass
    root.after(250, tick_hud)


def show_startup_loader():
    global startup_overlay
    startup_overlay = tk.Frame(root, bg="#02070b", highlightbackground=BLUE, highlightthickness=1)
    startup_overlay.place(relx=0.5, rely=0.5, relwidth=0.62, relheight=0.48, anchor="center")
    tk.Label(startup_overlay, text="J.A.R.V.I.S.", font=(FONT, 24, "bold"), fg=BLUE, bg="#02070b").pack(pady=(18, 2))
    tk.Label(startup_overlay, text="HYPERCORE INITIALIZATION", font=(FONT, 9, "bold"), fg=MAGENTA, bg="#02070b").pack()

    stage_label = tk.Label(startup_overlay, text="LINKING CORE SYSTEMS", font=(FONT, 8, "bold"), fg=GREEN, bg="#02070b")
    stage_label.pack(pady=(12, 4))
    progress_label = tk.Label(startup_overlay, text="00%  //  BOOT SEQUENCE", font=(FONT, 8, "bold"), fg=GOLD, bg="#02070b")
    progress_label.pack()

    scan = tk.Canvas(startup_overlay, width=470, height=225, bg="#02070b", highlightthickness=0)
    scan.pack(pady=(2, 8))

    boot_steps = [
        "LINKING CORE SYSTEMS",
        "SYNCING VOICE CHANNEL",
        "STABILIZING NETWORK",
        "READY FOR COMMAND",
    ]

    def advance(step=0, angle=0):
        if startup_overlay is None or not startup_overlay.winfo_exists():
            return

        scan.delete("all")
        cx, cy = 118, 106
        radius = 76
        progress = min(100, int((step / 44) * 100))

        for ring in (radius, radius - 18, radius - 36):
            scan.create_oval(cx - ring, cy - ring, cx + ring, cy + ring, outline="#123846", width=1)
        scan.create_line(cx - radius, cy, cx + radius, cy, fill="#123846")
        scan.create_line(cx, cy - radius, cx, cy + radius, fill="#123846")
        scan.create_arc(cx - radius + 10, cy - radius + 10, cx + radius - 10, cy + radius - 10,
                        start=angle, extent=220, style="arc", outline=BLUE, width=3)
        scan.create_arc(cx - radius + 24, cy - radius + 24, cx + radius - 24, cy + radius - 24,
                        start=angle + 90, extent=150, style="arc", outline=GREEN, width=2)
        scan.create_line(cx, cy, cx + math.cos(math.radians(angle)) * radius, cy + math.sin(math.radians(angle)) * radius, fill=GOLD, width=2)

        dot_a = math.radians(angle)
        dot_x = cx + math.cos(dot_a) * radius
        dot_y = cy + math.sin(dot_a) * radius
        pulse = 4 + (step % 5)
        scan.create_oval(dot_x - pulse, dot_y - pulse, dot_x + pulse, dot_y + pulse, outline=GREEN, width=2)
        scan.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill=BLUE, outline="")

        scan.create_text(264, 48, text="CORE DIAGNOSTICS", fill=BLUE, font=(FONT, 9, "bold"), anchor="w")
        diagnostics = ("NEURAL MESH   ONLINE", "VOICE CHANNEL LINKED", "MEMORY VAULT  SECURE", "UPLINK        STABLE")
        for index, line in enumerate(diagnostics):
            color = GREEN if index <= step // 12 else "#31535c"
            scan.create_rectangle(264, 67 + index * 21, 270, 73 + index * 21, fill=color, outline="")
            scan.create_text(280, 70 + index * 21, text=line, fill=color, font=(FONT, 8), anchor="w")

        bar_x, bar_y, bar_width = 264, 164, 174
        segments = 12
        for index in range(segments):
            x0 = bar_x + index * (bar_width / segments)
            color = BLUE if index < (progress * segments / 100) else "#0a2029"
            scan.create_rectangle(x0, bar_y, x0 + (bar_width / segments) - 3, bar_y + 12, fill=color, outline="")
        scan.create_text(bar_x, bar_y + 27, text="HYPERCORE CHARGE", fill=MUTED, font=(FONT, 7, "bold"), anchor="w")
        scan.create_text(bar_x + bar_width, bar_y + 27, text=f"{progress:02d}%", fill=GOLD, font=(FONT, 8, "bold"), anchor="e")

        stage_label.config(text=boot_steps[min(step // 7, len(boot_steps) - 1)])
        progress_label.config(text=f"{progress:02d}%  //  BOOT SEQUENCE")

        if step < 44:
            root.after(70, lambda: advance(step + 1, angle + 15))
        else:
            stage_label.config(text="READY FOR COMMAND")
            root.after(260, finish_startup_loader)

    advance()


def finish_startup_loader():
    global startup_overlay
    if startup_overlay is not None:
        startup_overlay.destroy()
        startup_overlay = None
    if VOICE_INPUT:
        threading.Thread(target=boot_voice_channel, daemon=True).start()


def boot_voice_channel():
    if root is not None:
        root.after(0, start_wake_listener)


def create_jarvis_window():
    global root, chat_area, input_box, status_label, history_list, jarvis_button, vision_button, ultron_button
    global vision_panel, weather_value, location_value, globe_canvas, listen_button, wake_button, attach_button, generate_button, model3d_button
    global clock_label, uptime_label, channel_label, neural_canvas, wave_canvas, wake_signal_canvas, wphase_label, session_started, location_status

    session_started = time.time()
    load_reminders()
    load_memories()
    load_tasks()
    load_calendar()
    root = tk.Tk()
    root.title("J.A.R.V.I.S.  //  MARK IV")
    root.geometry("1440x860")
    root.minsize(1180, 720)
    root.configure(bg=BG)

    sidebar = tk.Frame(root, width=258, bg=SIDEBAR, highlightbackground="#00a8b8", highlightthickness=1)
    sidebar.pack(side=tk.LEFT, fill=tk.Y)
    sidebar.pack_propagate(False)
    tk.Label(sidebar, text="J.A.R.V.I.S.", font=(FONT, 22, "bold"), fg=BLUE, bg=SIDEBAR).pack(pady=(22, 0))
    tk.Label(sidebar, text="MARK IV  ·  HYPERCORE", font=(FONT, 8), fg=MAGENTA, bg=SIDEBAR).pack()
    tk.Label(sidebar, text="STARK OS  //  BUILD 4.0.1", font=(FONT, 7), fg=MUTED, bg=SIDEBAR).pack(pady=(2, 12))

    ident = framed(sidebar, SIDEBAR)
    ident.pack(fill=tk.X, padx=12, pady=(0, 10))
    tk.Label(ident, text="OPERATOR", font=(FONT, 7), fg=MUTED, bg=SIDEBAR).pack(anchor="w", padx=8, pady=(6, 0))
    tk.Label(ident, text="SIR", font=(FONT, 12, "bold"), fg=GOLD, bg=SIDEBAR).pack(anchor="w", padx=8)
    tk.Label(ident, text="CLEARANCE  ·  LEVEL OMEGA", font=(FONT, 7), fg=GREEN, bg=SIDEBAR).pack(anchor="w", padx=8, pady=(0, 8))

    hud_button(sidebar, "＋  NEW SESSION", clear_chat).pack(fill=tk.X, padx=12, ipady=8)
    tk.Label(sidebar, text="SESSION ARCHIVE", font=(FONT, 8, "bold"), fg=MUTED, bg=SIDEBAR).pack(anchor="w", padx=16, pady=(18, 6))
    history_list = tk.Listbox(
        sidebar, bg="#04080d", fg="#9aabb2", selectbackground="#073f52", selectforeground=BLUE,
        relief=tk.FLAT, borderwidth=0, font=(FONT, 9), highlightthickness=1, highlightbackground="#123846",
    )
    history_list.pack(fill=tk.BOTH, expand=True, padx=12)

    meters = framed(sidebar, SIDEBAR)
    meters.pack(fill=tk.X, padx=12, pady=10)
    tk.Label(meters, text="VOICE CHANNEL", font=(FONT, 7, "bold"), fg=GOLD, bg=SIDEBAR).pack(anchor="w", padx=8, pady=(6, 1))
    wake_signal_canvas = tk.Canvas(meters, bg=SIDEBAR, highlightthickness=0, height=28)
    wake_signal_canvas.pack(fill=tk.X, padx=8, pady=(0, 4))
    tk.Label(meters, text="TELEMETRY", font=(FONT, 7, "bold"), fg=BLUE, bg=SIDEBAR).pack(anchor="w", padx=8, pady=(6, 2))
    neural_canvas = tk.Canvas(meters, bg=SIDEBAR, highlightthickness=0, height=28)
    neural_canvas.pack(fill=tk.X, padx=8)
    wave_canvas = tk.Canvas(meters, bg="#04080d", highlightthickness=0, height=40)
    wave_canvas.pack(fill=tk.X, padx=8, pady=(4, 8))

    main = tk.Frame(root, bg=BG)
    main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    topbar = tk.Frame(main, bg="#050a0f", height=72, highlightbackground="#00a8b8", highlightthickness=1)
    topbar.pack(fill=tk.X)
    topbar.pack_propagate(False)
    mode_frame = tk.Frame(topbar, bg="#050a0f")
    mode_frame.pack(side=tk.LEFT, padx=16, pady=14)
    jarvis_button = hud_button(mode_frame, "  JARVIS  ", lambda: switch_mode("jarvis"), bg="#00c8d8", fg="#000000")
    jarvis_button.pack(side=tk.LEFT, ipady=6, padx=(0, 6))
    vision_button = hud_button(mode_frame, "  VISION  ", lambda: switch_mode("vision"), fg=MUTED, bg="#0c1218")
    vision_button.pack(side=tk.LEFT, ipady=6)
    ultron_button = hud_button(mode_frame, "  ULTRON  ", lambda: switch_mode("ultron"), fg=MUTED, bg="#0c1218")
    ultron_button.pack(side=tk.LEFT, ipady=6, padx=(6, 0))

    mid = tk.Frame(topbar, bg="#050a0f")
    mid.pack(side=tk.LEFT, expand=True)
    channel_label = tk.Label(mid, text="CHANNEL  ·  PRIMARY / LINGUISTIC", font=(FONT, 8), fg=MUTED, bg="#050a0f")
    channel_label.pack(pady=(10, 0))
    status_label = tk.Label(mid, text="JARVIS  //  ONLINE  •  READY", font=(FONT, 10, "bold"), fg=GREEN, bg="#050a0f")
    status_label.pack()

    clocks = tk.Frame(topbar, bg="#050a0f")
    clocks.pack(side=tk.RIGHT, padx=18)
    clock_label = tk.Label(clocks, text="00:00:00", font=(FONT, 16, "bold"), fg=BLUE, bg="#050a0f")
    clock_label.pack(anchor="e")
    row = tk.Frame(clocks, bg="#050a0f")
    row.pack(anchor="e")
    uptime_label = tk.Label(row, text="UP 00:00:00", font=(FONT, 8), fg=MUTED, bg="#050a0f")
    uptime_label.pack(side=tk.LEFT, padx=(0, 10))
    wphase_label = tk.Label(row, text="W 0.00", font=(FONT, 8), fg=MAGENTA, bg="#050a0f")
    wphase_label.pack(side=tk.LEFT)
    location_status = tk.Label(row, text="LOC  ·  SCANNING", font=(FONT, 8), fg=GOLD, bg="#050a0f")
    location_status.pack(side=tk.LEFT, padx=(10, 0))

    workspace = tk.Frame(main, bg=BG)
    workspace.pack(fill=tk.BOTH, expand=True)
    center = tk.Frame(workspace, bg=BG)
    center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    right = tk.Frame(workspace, bg="#060b11", width=350, highlightbackground="#00a8b8", highlightthickness=1)
    right.pack(side=tk.RIGHT, fill=tk.Y)
    right.pack_propagate(False)

    chat_header = tk.Frame(center, bg=PANEL)
    chat_header.pack(fill=tk.X, padx=18, pady=(10, 0))
    tk.Label(chat_header, text="SECURE UPLINK", font=(FONT, 8, "bold"), fg=BLUE, bg=PANEL).pack(side=tk.LEFT, padx=8, pady=6)
    tk.Label(chat_header, text="AES-256  ·  NO LOG  ·  LOCAL CORE", font=(FONT, 7), fg=MUTED, bg=PANEL).pack(side=tk.RIGHT, padx=8)

    chat_area = scrolledtext.ScrolledText(
        center, wrap=tk.WORD, font=(FONT, 11), bg=PANEL, fg="#dddddd", insertbackground=BLUE,
        relief=tk.FLAT, padx=22, pady=18, highlightthickness=1, highlightbackground="#00a8b8",
    )
    chat_area.pack(fill=tk.BOTH, expand=True, padx=18, pady=(0, 8))
    chat_area.tag_config("jarvis_label", foreground=BLUE, font=(FONT, 10, "bold"))
    chat_area.tag_config("jarvis_text", foreground=TEXT)
    chat_area.tag_config("user_label", foreground=GREEN, font=(FONT, 10, "bold"))
    chat_area.tag_config("user_text", foreground="#ffffff")
    chat_area.tag_config("error_label", foreground=RED, font=(FONT, 10, "bold"))
    chat_area.tag_config("error_text", foreground="#ff8888")
    chat_area.tag_config("attachment", foreground="#00cfff")
    chat_area.insert(
        tk.END,
        "JARVIS  ·  BOOT\n"
        "Good day, Sir. Mark IV hypercore is online.\n"
        "Say Hey Jarvis, press VOICE, or keep WAKE ON for always-listening.\n"
        "4D global mesh is armed. Awaiting instruction.\n",
        "jarvis_text",
    )
    chat_area.config(state=tk.DISABLED)

    vision_panel = tk.Frame(center, bg=PANEL, highlightbackground=MAGENTA, highlightthickness=1)
    tk.Label(vision_panel, text="VISION  //  OPTICAL CORE", font=(FONT, 18, "bold"), fg=MAGENTA, bg=PANEL).pack(pady=(28, 4))
    tk.Label(vision_panel, text="IMAGE  ·  DOCUMENT  ·  SPECTRAL  ·  SYNTHESIS", font=(FONT, 9), fg="#647983", bg=PANEL).pack(pady=(0, 16))
    box = tk.Frame(vision_panel, bg=PANEL2, highlightbackground="#5a1a4a", highlightthickness=1)
    box.pack(fill=tk.BOTH, expand=True, padx=28, pady=10)
    tk.Label(
        box,
        text="VISION MODE ARMED\n\nATTACH  →  image / pdf / txt / csv\nGENERATE  →  diffusion render\n3D MODEL  →  interactive GLB\nCSV  →  live plot",
        font=(FONT, 11), fg="#9aabb2", bg=PANEL2, justify=tk.CENTER,
    ).place(relx=0.5, rely=0.5, anchor="center")

    tk.Label(right, text="4D GLOBAL CORE", font=(FONT, 10, "bold"), fg=BLUE, bg="#060b11").pack(pady=(14, 0))
    tk.Label(right, text="HYPERSPHERE  ·  TESSERACT CAGE", font=(FONT, 7), fg=MAGENTA, bg="#060b11").pack()
    globe_canvas = tk.Canvas(right, bg="#060b11", highlightthickness=0, bd=0, width=330, height=440)
    globe_canvas.pack(fill=tk.BOTH, expand=True, padx=4, pady=6)

    cards = framed(right, "#060b11")
    cards.pack(fill=tk.X, padx=10, pady=(0, 12))
    tk.Label(cards, text="GEOLOCK  ·  LIVE", font=(FONT, 7, "bold"), fg=MUTED, bg="#060b11").pack(anchor="w", padx=8, pady=(6, 0))
    location_value = tk.Label(cards, text="Acquiring node…", font=(FONT, 9), fg=BLUE, bg="#060b11", justify=tk.LEFT)
    location_value.pack(anchor="w", padx=8, pady=(2, 6))
    tk.Label(cards, text="ATMOSPHERICS", font=(FONT, 7, "bold"), fg=MUTED, bg="#060b11").pack(anchor="w", padx=8)
    weather_value = tk.Label(cards, text="Scanning live weather…", font=(FONT, 9), fg=BLUE, bg="#060b11", justify=tk.LEFT)
    weather_value.pack(anchor="w", padx=8, pady=(2, 6))
    loc_btns = tk.Frame(cards, bg="#060b11")
    loc_btns.pack(fill=tk.X, padx=8, pady=(0, 8))
    hud_button(loc_btns, "SET CITY", set_location_manual, fg=GOLD, bg="#14100a").pack(side=tk.LEFT, ipady=4)
    hud_button(loc_btns, "REFRESH", refresh_location, fg=GREEN, bg="#081810").pack(side=tk.LEFT, padx=(6, 0), ipady=4)

    dashboard = framed(right, "#060b11")
    dashboard.pack(fill=tk.X, padx=10, pady=(0, 12))
    tk.Label(dashboard, text="ASSISTANT DASHBOARD", font=(FONT, 7, "bold"), fg=BLUE, bg="#060b11").pack(anchor="w", padx=8, pady=(6, 0))
    dashboard_task_label = tk.Label(dashboard, text="TASKS  ·  0 active", font=(FONT, 8), fg=GREEN, bg="#060b11", anchor="w")
    dashboard_task_label.pack(anchor="w", padx=8, pady=(2, 0))
    dashboard_reminder_label = tk.Label(dashboard, text="REMINDERS  ·  0 queued", font=(FONT, 8), fg=GOLD, bg="#060b11", anchor="w")
    dashboard_reminder_label.pack(anchor="w", padx=8, pady=(2, 0))
    dashboard_event_label = tk.Label(dashboard, text="CALENDAR  ·  0 events", font=(FONT, 8), fg=BLUE, bg="#060b11", anchor="w")
    dashboard_event_label.pack(anchor="w", padx=8, pady=(2, 0))
    dashboard_memory_label = tk.Label(dashboard, text="MEMORY  ·  0 saved", font=(FONT, 8), fg=MAGENTA, bg="#060b11", anchor="w")
    dashboard_memory_label.pack(anchor="w", padx=8, pady=(2, 4))
    refresh_dashboard()

    console = tk.Frame(center, bg="#050a0f", highlightbackground="#00a8b8", highlightthickness=1)
    console.pack(fill=tk.X, padx=18, pady=(0, 12))
    tk.Label(console, text="COMMAND DECK", font=(FONT, 7, "bold"), fg=MUTED, bg="#050a0f").pack(anchor="w", padx=8, pady=(6, 2))
    inp = tk.Frame(console, bg="#050a0f")
    inp.pack(fill=tk.X, padx=8, pady=(0, 8))
    attach_button = hud_button(inp, "ATTACH", attach_file, fg=MUTED, bg=PANEL2)
    attach_button.config(state=tk.DISABLED)
    attach_button.pack(side=tk.LEFT, padx=(0, 6), ipady=10)
    generate_button = hud_button(inp, "GENERATE", generate_image, fg=MUTED, bg=PANEL2)
    generate_button.config(state=tk.DISABLED)
    generate_button.pack(side=tk.LEFT, padx=(0, 6), ipady=10)
    model3d_button = hud_button(inp, "3D MODEL", generate_3d_model, fg=MUTED, bg=PANEL2)
    model3d_button.config(state=tk.DISABLED)
    model3d_button.pack(side=tk.LEFT, padx=(0, 6), ipady=10)
    wake_button = hud_button(inp, "●  WAKE ON", toggle_wake_mode, fg=GREEN, bg="#03180e")
    wake_button.pack(side=tk.LEFT, padx=(0, 6), ipady=10)
    listen_button = hud_button(inp, "🎙  VOICE", listen_voice, fg=GREEN, bg=PANEL2)
    listen_button.pack(side=tk.LEFT, padx=(0, 6), ipady=10)
    input_box = tk.Text(
        inp, height=3, font=(FONT, 11), bg=PANEL2, fg="#ffffff", insertbackground=BLUE,
        relief=tk.FLAT, padx=10, pady=8, highlightthickness=1, highlightbackground=BLUE,
    )
    input_box.pack(side=tk.LEFT, fill=tk.X, expand=True)
    hud_button(inp, "  TRANSMIT  ", send_message, fg="#000000", bg=BLUE).pack(side=tk.RIGHT, padx=(7, 0), ipady=12)
    input_box.bind("<Return>", send_message)
    input_box.focus_set()
    switch_mode("jarvis")
    load_saved_location()
    apply_location_to_prompts()
    if location_info.get("city") and location_info.get("city") != "Unknown":
        push_location_ui()
    threading.Thread(target=get_location_and_weather, daemon=True).start()
    root.after(80, draw_globe)
    root.after(120, tick_hud)
    if VOICE_INPUT:
        show_startup_loader()
    else:
        root.after(1200, show_startup_loader)
    root.after(1000, check_reminders)
    root.mainloop()


def animate_access_rings(canvas, n=0):
    if access_window is None:
        return
    try:
        canvas.delete("ring")
        cx, cy = 260, 70
        now = time.time()
        for i in range(4):
            r = 18 + i * 16 + 6 * math.sin(now * 3 + i)
            canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=BLUE if i % 2 == 0 else MAGENTA, width=1, tags="ring")
        canvas.create_text(cx, cy, text="AUTH", fill=GOLD, font=(FONT, 9, "bold"), tags="ring")
        access_window.after(40, lambda: animate_access_rings(canvas, n + 1))
    except Exception:
        pass


access_window = tk.Tk()
access_window.title("J.A.R.V.I.S.  //  QUANTUM GATE")
access_window.geometry("540x520")
access_window.resizable(False, False)
access_window.configure(bg=BG)
tk.Label(access_window, text="J.A.R.V.I.S.", font=(FONT, 28, "bold"), fg=BLUE, bg=BG).pack(pady=(24, 0))
tk.Label(access_window, text="QUANTUM ACCESS GATE  ·  MARK IV", font=(FONT, 9), fg=MAGENTA, bg=BG).pack()
access_rings = tk.Canvas(access_window, bg=BG, highlightthickness=0, height=140)
access_rings.pack(fill=tk.X)
tk.Label(access_window, text="CLAP ONCE, OR ENTER / SPEAK ACCESS PHRASE", font=(FONT, 11, "bold"), fg="#ffffff", bg=BG).pack(pady=(4, 8))
access_entry = tk.Entry(
    access_window, font=(FONT, 13), bg=PANEL2, fg="#ffffff", insertbackground=BLUE,
    justify="center", relief=tk.FLAT, highlightthickness=1, highlightbackground=BLUE,
)
access_entry.pack(padx=70, fill=tk.X, ipady=12)
btn_row = tk.Frame(access_window, bg=BG)
btn_row.pack(pady=14)
hud_button(btn_row, "AUTHENTICATE", check_access, fg="#000000", bg=BLUE).pack(side=tk.LEFT, padx=6, ipadx=12, ipady=8)
access_voice_button = hud_button(btn_row, "SPEAK PHRASE", listen_access_phrase, fg=GREEN, bg="#081810")
access_voice_button.pack(side=tk.LEFT, padx=6, ipadx=12, ipady=8)
access_status = tk.Label(access_window, text="AWAITING CLAP OR ACCESS PHRASE", font=(FONT, 9, "bold"), fg=MUTED, bg=BG)
access_status.pack()
tk.Label(access_window, text="The gate listens quietly for one sharp clap", font=(FONT, 8), fg=MUTED, bg=BG).pack(pady=(8, 0))
access_entry.bind("<Return>", check_access)
access_entry.focus_set()
access_window.after(80, lambda: animate_access_rings(access_rings))
if VOICE_INPUT:
    access_window.after(300, start_access_clap_listener)
try:
    access_window.mainloop()
except Exception as _boot_err:
    _fatal("Crash while running:\n%s\n\n%s" % (_boot_err, traceback.format_exc()))
