import datetime
import time
import json
import threading
import os
import win32gui
import win32process
import win32api
import win32con
import matplotlib.pyplot as plt

DATA_FILE = "screen_time_data.json"
APP_CATEGORIES = {
    "chrome.exe": "Browser",
    "msedge.exe": "Browser",
    "firefox.exe": "Browser",
    "code.exe": "Code Editor",
    "pycharm64.exe": "Code Editor",
    "cmd.exe": "Terminal",
    "powershell.exe": "Terminal",
    "explorer.exe": "File Manager",
    "word.exe": "Document",
    "excel.exe": "Spreadsheet",
    "powerpnt.exe": "Presentation",
    "spotify.exe": "Music",
}

def get_active_window_title():
    active_window = win32gui.GetForegroundWindow()
    pid = win32process.GetWindowThreadProcessId(active_window)
    process_handle = win32api.OpenProcess(
        win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
        False,
        pid[1]
    )
    exe_path = win32process.GetModuleFileNameEx(process_handle, 0)
    win32api.CloseHandle(process_handle)
    app_name = exe_path.split("\\")[-1].lower()
    category = APP_CATEGORIES.get(app_name, "Other")
    return app_name, category

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

tracking = False

def track_screen_time(interval_seconds=5):
    global tracking
    tracking = True
    data = load_data()
    last_window, last_time = None, datetime.datetime.now()

    while tracking:
        current_window, category = get_active_window_title()
        now = datetime.datetime.now()

        if last_window is not None:
            duration = (now - last_time).total_seconds()
            if current_window != last_window:
                if last_window not in data:
                    data[last_window] = {"duration": 0, "category": category}
                data[last_window]["duration"] += duration
                save_data(data)
                last_time = now

        last_window = current_window
        time.sleep(interval_seconds)

def start_tracking():
    t = threading.Thread(target=track_screen_time, daemon=True)
    t.start()
    print("Tracking started in background...")

def stop_tracking():
    global tracking
    tracking = False
    print("Tracking stopped.")

def plot_bar_chart():
    data = load_data()
    sorted_data = sorted(data.items(), key=lambda x: x[1]["duration"], reverse=True)
    apps = [app for app, _ in sorted_data]
    durations = [round(info["duration"] / 60, 2) for _, info in sorted_data]

    plt.figure(figsize=(10, 6))
    plt.barh(apps, durations, color='skyblue')
    plt.xlabel("Screen Time (minutes)")
    plt.ylabel("Applications")
    plt.title("Screen Time Tracker - Bar Chart")
    plt.gca().invert_yaxis()
    for i, v in enumerate(durations):
        plt.text(v + 0.1, i, f"{v} min", va='center')
    plt.show()

def plot_pie_chart():
    data = load_data()
    category_durations = {}
    for info in data.values():
        category = info["category"]
        category_durations[category] = category_durations.get(category, 0) + info["duration"]

    categories = list(category_durations.keys())
    durations = [d / 60 for d in category_durations.values()]

    plt.figure(figsize=(8, 8))
    plt.pie(durations, labels=categories, autopct="%1.1f%%", startangle=140)
    plt.title("Screen Time Tracker - Pie Chart")
    plt.axis("equal")
    plt.show()
if __name__ == "__main__":
    start_tracking()
    input("Press Enter to stop tracking...\n")
    stop_tracking()
    plot_bar_chart()
    plot_pie_chart()
