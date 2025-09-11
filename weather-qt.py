import requests
import feedparser
import re
import html
from PyQt5.QtWidgets import QApplication, QWidget
import datetime
import os
import tts_helper
import source_helper
import time
import threading
from flask import Flask, url_for, request
import browser_helper
from flask_socketio import SocketIO
import signal
import os
import sys

app = QApplication(sys.argv)

current_version = "WeatherPeg Version 2.5"
designed_by = "Designed by Diode-exe"


def fetch_initial_weather_globals():
    global current_title, current_summary, current_link, warning_title, warning_summary
    try:
        response = requests.get(source_helper.RSS_URL)
        feed = feedparser.parse(response.content)
        for entry in feed.entries:
            if entry.category == "Warnings and Watches":
                if not entry.summary == "No watches or warnings in effect.":
                    warning_summary = entry.summary
                if entry.summary == "No watches or warnings in effect.":
                    warning_summary = "No watches or warnings in effect."
                warning_title = entry.title
        for entry in feed.entries:
            if entry.category == "Current Conditions":
                current_title = entry.title
                current_link = entry.link
                current_summary = html.unescape(entry.summary)
                current_summary = re.sub(r'<[^>]+>', '', current_summary)
                break
    except Exception as e:
        print(f"[ERROR] Could not fetch initial weather: {e}")

class Config():
    def get_config_bool(key):
        configfilename = "txt/config.txt"
        try:
            with open(configfilename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}:"):
                        value = line.split(":", 1)[1].strip()
                        # Convert to boolean (0 = False, 1 = True)
                        return value == "1"
        except FileNotFoundError:
            print(f"[LOG] File {configfilename} not found")
            return False
        return False  # Default to False if not found

    def get_config_port():
        configfilename = "txt/config.txt"
        try:
            with open(configfilename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.lower().startswith("port:"):
                        value = line.split(":", 1)[1].strip()
                        try:
                            return int(value)  # return as integer
                        except ValueError:
                            print(f"[LOG] Invalid port value: {value}")
                            return None
        except FileNotFoundError:
            print(f"[LOG] File {configfilename} not found")
            return None
        
        return None  # Default if "port:" not found

port = Config.get_config_port()

# def display():
#     global root, title_var, summary_var, link_var, scrolling_summary, timestamp_var, warning_var, current_warning, current_fact_var, warning_title_var
#     global display_flash
#     global refresh_button, fullscreen_button, instructions

#     if Config.get_config_bool("show_display"):

#         root = tk.Tk()
#         root.title("WeatherPeg")
#         root.configure(bg="black")
#         root.geometry("800x600")

#         # Fullscreen keybindings
#         root.bind("<F11>", ScreenState.toggle_fullscreen)
#         root.bind("<Escape>", ScreenState.exit_fullscreen)
#         root.bind("<F5>", WeatherFunctions.refresh_weather)
#         root.bind("<F6>", CommandWindow.create_command_window)
#         root.bind("<F4>", lambda event: browser_helper.WebOpen.opener(port))

#         # Create StringVar variables
#         title_var = tk.StringVar(value=current_title)
#         link_var = tk.StringVar(value=current_link)
#         warning_var = tk.StringVar(value=warning_summary)
#         warning_title_var = tk.StringVar(value=warning_title)
#         # current_fact_var = tk.StringVar(value=current_fact)

#         # Create and pack labels
#         title_label = tk.Label(root, textvariable=title_var, fg="lime", bg="black",
#                             font=("Courier", 16, "bold"), justify="left",
#                             padx=10, pady=10, wraplength=750)
#         title_label.pack()

#         # Create scrolling summary (replaces the old summary_label)
#         scrolling_summary = ScrollingSummary(root, current_summary, width=80, speed=150)

#         if Config.get_config_bool("show_link"):
#             print("[LOG] Showing link")
#             link_label = tk.Label(
#                 root, textvariable=link_var, 
#                 fg="cyan", bg="black",
#                 font=("Courier", 10), justify="left",
#                 padx=10, pady=10
#             )
#             link_label.pack()
#         else:
#             print("[LOG] Not showing link")

#         version_label = tk.Label(
#             root, text=current_version, 
#             fg="cyan", bg="black",
#             font=("Courier", 10), justify="left"
#         )
#         version_label.pack(side=tk.BOTTOM, pady=10, padx=10)
        
#         designed_by_label = tk.Label(
#             root, text=designed_by, 
#             fg="cyan", bg="black",
#             font=("Courier", 10), justify="left"
#         )
#         designed_by_label.pack(side=tk.BOTTOM, pady=10, padx=10)

#         if Config.get_config_bool("show_warning"):
#             print("[LOG] Showing warning label")
#             show_warnings = True
#             current_warning_title = tk.Label(
#                 root, textvariable=warning_title_var, 
#                 fg="lime", bg="black",
#                 font=("Courier", 16, "bold"), justify="left",
#                 padx=10, pady=10, wraplength=750
#             )
#             current_warning_title.pack()

#             current_warning = tk.Label(
#                 root, textvariable=warning_var, 
#                 fg="lime", bg="black",
#                 font=("Courier", 16, "bold"), justify="left",
#                 padx=10, pady=10, wraplength=750
#             )
#             current_warning.pack()
#         else:
#             print("[LOG] Not showing warning labels")
#             show_warnings = False

#         # fact_label = tk.Label(root, textvariable=current_fact_var, fg="lime", bg="black",
#         #                 font=("Courier", 16, "bold"), justify="left",
#         #                 padx=10, pady=10, wraplength=750)

#         # fact_label.pack()

#         if Config.get_config_bool("show_buttons"):
#             print("[LOG] Showing buttons")
#             refresh_button = tk.Button(
#                 root, text="Refresh Weather (F5)", 
#                 command=WeatherFunctions.refresh_weather,
#                 bg="green", fg="yellow", font=("Courier", 12)
#             )
#             refresh_button.pack(pady=10)

#             fullscreen_button = tk.Button(
#                 root, text="Toggle Fullscreen (F11)", 
#                 command=ScreenState.toggle_fullscreen,
#                 bg="blue", fg="white", font=("Courier", 12)
#             )
#             fullscreen_button.pack(pady=5)

#             browser_button = tk.Button(
#                 root, text="Open webserver page (F4)", 
#                 command=lambda: browser_helper.WebOpen.opener(port),
#                 bg="blue", fg="white", font=("Courier", 12)
#             )
#             browser_button.pack(pady=5)

#             # forecast_button = tk.Button(root, text="5 Day Forecast", command=process_weather_entries,
#             #                     bg="blue", fg="white", font=("Courier", 12))
#             # forecast_button.pack(pady=5)
#             show_buttons = True
#         else:
#             print("[LOG] Not showing buttons")
#             show_buttons = False

#         if Config.get_config_bool("show_instruction"):
#             print("[LOG] Showing instruction")
#             show_instructions = True
#             # Add instructions
#             instructions = tk.Label(
#                 root, text="Press F11 to toggle fullscreen • Press Escape to exit fullscreen",
#                 fg="gray", bg="black",
#                 font=("Courier", 10)
#             )
#             instructions.pack(pady=5)
#         else:
#             print("[LOG] Not showing instruction")
#             show_instructions = False

#         # Add timestamp
#         timestamp_var = tk.StringVar()
#         timestamp_label = tk.Label(
#             root, textvariable=timestamp_var,
#             fg="yellow", bg="black",
#             font=("Courier", 10)
#         )
#         timestamp_label.pack(side=tk.BOTTOM, pady=10)

#         def update_timestamp():
#             timestamp_var.set(f"Current time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#             root.after(1000, update_timestamp)  # Update every second

#         update_timestamp()

#         # Set up automatic refresh every 2 minutes
#         def auto_refresh():
#             WeatherFunctions.refresh_weather()
#             timestamp_var.set(f"Auto-refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
#             root.after(120000, auto_refresh)  # 120000 ms = 2 minutes

#         def display_flash():
#             title_label.config(fg="black")
#             link_label.config(fg="black")
#             scrolling_summary.flash_black()  # Flash the scrolling summary
#             if show_instructions:
#                 instructions.config(fg="black")
#             timestamp_label.config(fg="black")
#             if show_buttons:
#                 refresh_button.config(bg="black", fg="black", bd=0, highlightthickness=0)
#                 fullscreen_button.config(bg="black", fg="black", bd=0, highlightthickness=0)
#                 browser_button.config(fg="black", bg="black", bd=0, highlightthickness=0)
#             link_label.config(fg="black")
#             if show_warnings:
#                 current_warning.config(fg="black")
#                 current_warning_title.config(fg="black")
#             version_label.config(fg="black", bg="black")
#             designed_by_label.config(fg="black", bg="black")
#             # fact_label.config(fg="black")

#             # Use after() instead of sleep
#             root.after(750, restore_colors)

#         def restore_colors():
#             title_label.config(fg="lime")
#             link_label.config(fg="cyan")
#             if show_instructions:
#                 instructions.config(fg="gray")
#             timestamp_label.config(fg="yellow")
#             if show_buttons:
#                 refresh_button.config(bg="green", fg="yellow", bd=1, highlightthickness=1)
#                 fullscreen_button.config(bg="blue", fg="white", bd=1, highlightthickness=1)
#                 browser_button.config(bg="blue", fg="white", bd=1, highlightthickness=1)
#             link_label.config(fg="cyan")
#             if show_warnings:
#                 current_warning.config(fg="lime")
#                 current_warning_title.config(fg="lime")
#             version_label.config(fg="cyan", bg="black")
#             designed_by_label.config(fg="cyan", bg="black")
#             # fact_label.config(fg="lime")

#         if Config.get_config_bool("show_cmd"):
#             print("[LOG] Showing command window")
#             CommandWindow.create_command_window()
#         else:
#             print("[LOG] Not showing command window")

#         # Schedule flashes every 10 minutes
#         def schedule_flash():
#             display_flash()
#             root.after(600000, schedule_flash)  # 10 minutes

#         # Start the flash cycle
#         root.after(600000, schedule_flash)

#         root.after(120000, auto_refresh)  # Start auto-refresh after 2 minutes

#         weathermodechoice()

#         root.mainloop()

class MainWindow():
    window = QWidget()
    
    window.show()

app.exec()


if __name__ == "__main__":
    print(f"Welcome to WeatherPeg, version {current_version}")
    print("Fetching initial weather data for webserver...")
    fetch_initial_weather_globals()
    if Config.get_config_bool("show_display"):
        print("Starting GUI...")
        display()
    else: 
        print("[LOG] Not showing display")
        while True:
            time.sleep(1)

