import customtkinter as ctk
from tkinter import messagebox
import datetime
import json
import threading
import time
from win10toast import ToastNotifier
from winotify import Notification, audio
import winsound

import pystray
from PIL import Image, ImageDraw
import sys

import os
import time

# -------------------------
# Init
# -------------------------
toaster = ToastNotifier()
FILE_NAME = "reminders.json"
reminders = []
sound_path = os.path.join(os.path.dirname(__file__), "alert.wav")
# -------------------------
# Load / Save
# -------------------------
def load_reminders():
    try:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    except:
        return []

def save_reminders():
    with open(FILE_NAME, "w") as f:
        json.dump(reminders, f, indent=4)

# -------------------------
# Tray icon
# -------------------------
def create_image():
    img = Image.new('RGB', (64, 64), color=(30, 30, 30))
    d = ImageDraw.Draw(img)
    d.rectangle((16, 16, 48, 48), fill=(0, 200, 255))
    return img

def show_window(icon, item):
    app.after(0, app.deiconify)

def quit_app(icon, item):
    icon.stop()
    app.after(0, app.destroy)
    sys.exit()

def run_tray():
    icon = pystray.Icon(
        "ReminderApp",
        create_image(),
        "Reminder App",
        menu=pystray.Menu(
            pystray.MenuItem("Open", show_window),
            pystray.MenuItem("Exit", quit_app)
        )
    )
    icon.run_detached()

# -------------------------
# Notification
# -------------------------
def notify(msg):
    toast = Notification(
        app_id="URAM Reminder",
        title="Reminder",
        msg=msg
    )

    toast.set_audio(audio.Default, loop=False)
    toast.show()

    winsound.PlaySound(sound_path, winsound.SND_FILENAME)
# -------------------------
# Background reminder loop
# -------------------------
def reminder_loop():
    triggered = set()

    while True:
        now = datetime.datetime.now()

        for r in reminders[:]:
            try:
                r_time = datetime.datetime.strptime(r["time"], "%Y-%m-%d %H:%M")
            except:
                continue

            if r["time"] not in triggered:
                diff = (r_time - now).total_seconds()

                if 0 <= diff < 30:
                    notify(r["message"])
                    triggered.add(r["time"])

                    # optional: remove after firing
                    # reminders.remove(r)
                    # save_reminders()

        time.sleep(10)

# -------------------------
# UI actions
# -------------------------
def add_reminder():
    date = date_entry.get()
    time_str = time_entry.get()
    msg = message_entry.get()

    try:
        dt = datetime.datetime.strptime(f"{date} {time_str}", "%Y-%m-%d %H:%M")
    except:
        messagebox.showerror("Error", "Invalid date/time format")
        return

    reminder = {
        "time": dt.strftime("%Y-%m-%d %H:%M"),
        "message": msg
    }

    reminders.append(reminder)
    save_reminders()
    update_list()

def delete_selected():
    selected = listbox.get()
    if not selected:
        return

    for r in reminders:
        if f"{r['time']} - {r['message']}" == selected:
            reminders.remove(r)
            break

    save_reminders()
    update_list()

def update_list():
    listbox.configure(values=[
        f"{r['time']} - {r['message']}" for r in reminders
    ])

# -------------------------
# Window behavior
# -------------------------
def on_closing():
    app.withdraw()  # hide instead of close

# -------------------------
# Init app
# -------------------------
reminders = load_reminders()

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Reminder App")
app.geometry("500x400")

app.protocol("WM_DELETE_WINDOW", on_closing)

# start hidden (important for tray apps)
app.withdraw()

# -------------------------
# UI
# -------------------------
date_entry = ctk.CTkEntry(app, placeholder_text="YYYY-MM-DD")
date_entry.pack(pady=5)

time_entry = ctk.CTkEntry(app, placeholder_text="HH:MM")
time_entry.pack(pady=5)

message_entry = ctk.CTkEntry(app, placeholder_text="Reminder message")
message_entry.pack(pady=5)

add_btn = ctk.CTkButton(app, text="Add Reminder", command=add_reminder)
add_btn.pack(pady=10)

listbox = ctk.CTkComboBox(app, values=[])
listbox.pack(pady=10)

delete_btn = ctk.CTkButton(app, text="Delete Selected", command=delete_selected)
delete_btn.pack(pady=5)

update_list()

# -------------------------
# Start background systems
# -------------------------
threading.Thread(target=reminder_loop, daemon=True).start()
threading.Thread(target=run_tray, daemon=True).start()

# -------------------------
# Run app
# -------------------------
app.mainloop()