import tkinter as tk
import source_helper
import requests
import feedparser
import subprocess, sys
from win11toast import toast
import threading
import os
import datetime

global response, feed, warning_title, warning_summary, current_title, title_var, warning_title_var

current_version = "WeatherPeg Version 3.0"

def dldata(event=None):
    print("[LOG] Getting new data...")
    response = requests.get(source_helper.RSS_URL)
    feed = feedparser.parse(response.content)
    for entry in feed.entries:
        if entry.category == "Current Conditions":
            current_title = entry.title

            for entry in feed.entries:
                if entry.category == "Warnings and Watches":
                    if not entry.summary == "No watches or warnings in effect.":
                        warning_summary = entry.summary
                    if entry.summary == "No watches or warnings in effect.":
                        warning_summary = "No watches or warnings in effect."
                    warning_title = entry.title
                    if not "No watches" in warning_title:
                        threading.Thread(target=threading_warning_notif, daemon=True).start()

def threading_warning_notif(event=None):
    threading.Thread(target=warning_notif, daemon=True).start()

def warning_notif(event=None):
    toast("Weather Warning!", "WeatherPeg has detected a potential weather warning or watch!")
    
def logger():
        filename = "txt/history.txt"
        logged_time = (f"Current time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        if os.path.exists(filename):
            print(f"[LOG] Found {filename}")
        else:
            print(f"[LOG] Could not find {filename}, but created it")
            with open(filename, "a") as f:
                f.write(f"{current_title}\n")
                f.write(f"Current warning: {warning_title}\n")
                f.write(f"Logged time: {logged_time}\n")
                f.write("This was written with WeatherPeg Desktop Widget")
                f.write("-" * 50 + "\n")
            print(f"[LOG] Logged current weather to {filename}")

response = requests.get(source_helper.RSS_URL)
feed = feedparser.parse(response.content)
for entry in feed.entries:
    if entry.category == "Current Conditions":
        current_title = entry.title

        for entry in feed.entries:
            if entry.category == "Warnings and Watches":
                if not entry.summary == "No watches or warnings in effect.":
                    warning_summary = entry.summary
                if entry.summary == "No watches or warnings in effect.":
                    warning_summary = "No watches or warnings in effect."
                warning_title = entry.title
                logger()

def refresh_weather(event=None):
    dldata()
    title_var.set(current_title)
    warning_title_var.set(warning_title)

def open_large_program(event=None):
    print("Opening main program...")
    subprocess.Popen(["python", "weather-cmd.py"])
    sys.exit()

print("Welcome to the WeatherPeg Desktop Widget")

root = tk.Tk()
root.title("WeatherPeg Widget")
root.configure(bg="black")
root.geometry("")

root.bind("<F5>", lambda event: refresh_weather())
root.bind("<F8>", open_large_program)
# root.bind("<F9>", threading_warning_notif)

warning_title_var = tk.StringVar(value=warning_title)

warning_summary_var = tk.StringVar(value=warning_summary)

words_to_remove = ["Current", "Conditions:"]

current_title = " ".join(word for word in current_title.split() if word not in words_to_remove)

print(current_title)
print(warning_title)

warning_title_label = tk.Label(root, textvariable=warning_title_var, fg="lime", bg="black",
                    font=("Courier", 11, "bold"), justify="left")
warning_title_label.pack()

# warning_summary_label = tk.Label(root, textvariable=warning_summary_var, fg="lime", bg="black",
#                     font=("Courier", 16, "bold"), justify="left")
# warning_summary_label.pack()

title_var = tk.StringVar(value=current_title)

title_label = tk.Label(root, textvariable=title_var, fg="lime", bg="black",
                    font=("Courier", 16, "bold"), justify="left")
title_label.pack()

version_label = tk.Label(
    root, text=current_version, 
    fg="cyan", bg="black",
    font=("Courier", 10), justify="left"
)
version_label.pack(side=tk.BOTTOM, pady=10, padx=10)

root.mainloop()
