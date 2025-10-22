import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import feedparser
import re
import html
import tkinter as tk
import datetime
import os, sys
if os.name == "nt":
    import tts_helper
    from win11toast import toast
else:
    logging.info("Not importing tts, toast, not on NT")
import source_helper
import time
import threading
from flask import Flask, url_for, request, render_template
import browser_helper
from flask_socketio import SocketIO
import signal
import radar_helper
import logging

# https://github.com/Diode-exe/WeatherPeg

# Global variables to store weather data
current_entry = None
current_title = ""
current_summary = ""
current_link = ""
warning_summary = ""
warning_title = ""

# Global GUI variables
root = None
title_var = None
summary_var = None
link_var = None

current_version = "WeatherPeg Version 3.3.1"
designed_by = "Designed by Diode-exe"
prog = "WeatherPeg"

# Create a single shared HTTP session with retries/timeouts
def _create_http_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

_HTTP_SESSION = _create_http_session()

def http_get(url, **kwargs):
    timeout = kwargs.pop("timeout", 10)
    return _HTTP_SESSION.get(url, timeout=timeout, **kwargs)

class ScrollingSummary:
    # garbage implementation, i hate this
    def __init__(self, parent, text="", width=80, speed=150):
        self.original_text = text
        self.width = width
        self.speed = speed
        self.position = 0
        self.is_scrolling = False
        self.after_id = None  # Track the scheduled callback
        self.scroll_id = 0  # Unique ID for each scroll session
        self.label = tk.Label(parent, text="", fg="lime", bg="black",
                            font=("VCR OSD Mono", 12), justify="left",
                            padx=10, pady=10)
        self.label.pack()
        self.update_text(text)

    def update_text(self, new_text):
        # Stop any existing scrolling by incrementing scroll_id
        self.scroll_id += 1
        self.is_scrolling = False

        # Cancel any pending after callbacks
        if self.after_id:
            self.label.after_cancel(self.after_id)
            self.after_id = None

        self.original_text = new_text
        self.position = 0

        # Only scroll if text is longer than display width
        if len(new_text) <= self.width:
            self.label.config(text=new_text)
        else:
            self.is_scrolling = True
            current_scroll_id = self.scroll_id
            self.scroll(current_scroll_id)

    def scroll(self, scroll_id):
        # Check if this scroll session is still valid
        if scroll_id != self.scroll_id or not self.is_scrolling or not self.original_text:
            return

        # Create extended text with spacing for smooth looping
        extended_text = self.original_text + "   ***   "
        # Calculate visible portion
        start = self.position % len(extended_text)
        display_text = (extended_text[start:] + extended_text)[:self.width]
        self.label.config(text=display_text)
        # Move position for next update
        self.position += 1
        # Schedule next update with the same scroll_id
        self.after_id = self.label.after(self.speed, lambda: self.scroll(scroll_id))

    def flash_black(self):
        """Flash the label white for refresh indication"""
        self.label.config(fg="black")
        self.label.after(750, lambda: self.label.config(fg="lime"))

def update_display():
    """Update the GUI with current weather data"""
    global title_var, summary_var, link_var, scrolling_summary, warning_var
    if title_var and summary_var and link_var:
        title_var.set(current_title)
        link_var.set(current_link)
        warning_var.set(warning_summary)
        warning_title_var.set(warning_title)
        # Update the scrolling summary
        if scrolling_summary:  # Fixed reference
            scrolling_summary.update_text(current_summary)


class WeatherFunctions():
    # this does not use self, for the record
    def update_forecast():
        title_var.set(current_title)
        if Config.get_config_bool("show_scroller"):
            scrolling_summary.update_text(current_summary)
        warning_var.set("")
        warning_title_var.set("")

    def refresh_weather(event=None):
        """Refresh weather data and update display"""
        fetch_initial_weather_globals()
        weathermodechoice()
        logger()
        # random_fact()
        # current_fact_var.set(current_fact)
        display_flash()
        update_display()
        socketio.emit("weather_updated")

class ScreenState():
    def toggle_fullscreen(event=None):
        """Toggle fullscreen mode"""
        global root
        current_fullscreen = root.attributes("-fullscreen")
        root.attributes("-fullscreen", not current_fullscreen)

        # # Show elements when exiting fullscreen, hide when entering
        # if current_fullscreen:  # Was fullscreen, now exiting
        #     show_elements()
        # else:  # Was windowed, now entering fullscreen
        #     hide_elements()

    def exit_fullscreen(event=None):
        """Exit fullscreen mode"""
        global root
        root.attributes("-fullscreen", False)
        # show_elements()

def logger():
    if Config.get_config_bool("write_log"):
        filename = "txt/history.txt"
        logged_time = timestamp_var.get()
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        if os.path.exists(filename):
            logging.info(f"Found {filename}")
        else:
            logging.info(f"Could not find {filename}, but created it")
        with open(filename, "a") as f:
                f.write(f"{current_title}\n")
                f.write(f"Summary: {current_summary}\n")
                f.write(f"Coords/Link: {current_link}\n")
                f.write(f"Current warning: {warning_summary}\n")
                f.write(f"Logged time: {logged_time}\n")
                f.write("-" * 50 + "\n")
        logging.info(f"Logged current weather to {filename}")
    else:
        logging.info("Not writing to log")

# def random_fact():
#     global current_fact
#     facts = [
#         "Did you know lighting strikes the earth about 100 times a second?",
#         "You're watching WeatherPeg, the one-stop shop for Winnipeg's weather!",
#         "Vaccines cause autism",
#         "The Earth is flat",
#         "Chemtrails are real",
#         "They manipulate the weather",
#         "A raindrop falls at about 7 mph - slower than you walk!",
#         "Snowflakes have six sides, but no two are exactly alike!",
#         "Stay tuned for more totally radical weather updates!",
#         "The liberals are brainwashed",
#         "They know the cure for cancer",
#         "90 percent of internet users are bots",
#         "9/11 was an inside job",
#         "COVID was a crisis response simulation",
#         "COVID vaccines are deadly"
#     ]
#     current_fact = random.choice(facts)

# random_fact()


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
            logging.error(f"File {configfilename} not found")
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
                            logging.error(f"Invalid port value: {value}")
                            return None
        except FileNotFoundError:
            logging.error(f"File {configfilename} not found")
            return None

        return None  # Default if "port:" not found

    def get_config_value(key, default=None):
        configfilename = "txt/config.txt"
        try:
            with open(configfilename, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith(f"{key}:"):
                        value = line.split(":", 1)[1].strip()
                        # Try to convert to int if possible
                        if value.isdigit():
                            return int(value)
                        try:
                            return float(value)  # handles decimal numbers
                        except ValueError:
                            return value  # fallback to raw string
        except FileNotFoundError:
            logging.error(f"File {configfilename} not found")
            return default
        return default

if Config.get_config_port() in range(1, 65535):
    port = Config.get_config_port()
else:
    logging.error("Webserver port not valid!")

def main_speaker(text):
    if os.name == "nt":
        tts_enabled = Config.get_config_bool("do_tts")
        logging.info(f"TTS enabled: {tts_enabled}")
        if tts_enabled:
            logging.info(f"About to speak: {text}")
            tts_helper.speaker(text)
        else:
            logging.info("TTS is disabled in config")
    else:
        if check_espeak():
            thread = threading.Thread(target=linux_tts, args=(text,))
            thread.daemon = True
            thread.start()
        else:
            logging.info(f"TTS not available - espeak not found. Install with: sudo apt install espeak")

def weathermodechoice():
    if Config.get_config_bool("mode"):
        def get_weather():
            # mode 1
            # Fetch fresh data
            response = http_get(source_helper.RSS_URL)
            feed = feedparser.parse(response.content)

            for entry in feed.entries:
                if entry.category == "Warnings and Watches":
                    if not entry.summary == "No watches or warnings in effect.":
                        warning_summary = entry.summary
                    if entry.summary == "No watches or warnings in effect.":
                        warning_summary = "No watches or warnings in effect."
                    warning_title = entry.title
                    if not "No watches" in warning_title:
                        threading.Thread(target=threading_warning_notif, daemon=True).start()

            for entry in feed.entries:
                if entry.category == "Current Conditions":
                    global title_var, link_var, warning_var, warning_title_var
                    current_title = entry.title
                    current_link = entry.link

                    # Decode HTML entities and clean text
                    current_summary = html.unescape(entry.summary)
                    current_summary = re.sub(r'<[^>]+>', '', current_summary)

                    print("Current Conditions Updated:")
                    print("Entry title:", current_title)
                    print("Entry summary:", current_summary)
                    print("Entry link:", current_link)
                    print("-" * 50)
                    if Config.get_config_bool("show_display"):
                        title_var.set(current_title)
                        link_var.set(current_link)
                        warning_var.set(warning_summary)
                        warning_title_var.set(warning_title)
                        if Config.get_config_bool("show_scroller"):
                            scrolling_summary.update_text(current_summary)
                        break
            if os.name == "nt":
                if Config.get_config_bool("do_tts"):
                    tts_helper.speaker(current_title)
                    tts_helper.speaker(current_summary)
                    tts_helper.speaker(warning_title)
                    tts_helper.speaker(warning_summary)
            else:
                if check_espeak():
                    if Config.get_config_bool("do_tts"):
                        tts_helper.linux_tts(current_title)
                        tts_helper.linux_tts(current_summary)
                        tts_helper.linux_tts(warning_title)
                        tts_helper.linux_tts(warning_summary)
                else:
                    logging.error(f"TTS not available - espeak not found. Install with: sudo apt install espeak")

            dlhistory()

        get_weather()
        update_display()
    else:
        # mode 0
        def cycle_weather_entries():
            def background_cycle():
                index = 0

                while True:
                    try:
                        # Fetch fresh data each cycle
                        try:
                            response = http_get(source_helper.RSS_URL)
                        except Exception as e:
                            logging.error(f"Error in getting weather data")
                        feed = feedparser.parse(response.content)
                        weather_entries = [entry for entry in feed.entries if entry.category == "Weather Forecasts"]

                        if weather_entries:
                            global warning_summary
                            entry = weather_entries[index]
                            current_title = entry.title
                            current_link = entry.link
                            current_summary = html.unescape(entry.summary)
                            current_summary = re.sub(r'<[^>]+>', '', current_summary)

                            warning_summary = current_summary

                            print("Current Conditions Updated:")
                            print("Entry title:", current_title)
                            print("Entry summary:", current_summary)
                            print("Entry link:", current_link)
                            print("-" * 50)

                            if os.name == "nt":
                                if Config.get_config_bool("do_tts"):
                                    tts_helper.speaker(current_title)
                                    tts_helper.speaker(current_summary)
                            else:
                                if check_espeak():
                                    tts_helper.linux_tts(current_title)
                                    tts_helper.linux_tts(current_summary)
                                else:
                                    logging.error(f"TTS not available - espeak not found. Install with: sudo apt install espeak")

                            index = (index + 1) % len(weather_entries)

                            # Schedule GUI update on main thread
                            if 'root' in globals() and root:
                                root.after(0, update_display)
                    except Exception as e:
                        logging.error(f"Error in weather cycle: {e}")

                    time.sleep(30)

            thread = threading.Thread(target=background_cycle)
            thread.daemon = True
            thread.start()

        cycle_weather_entries()
pass

refresh_delay = Config.get_config_value("refresh_delay", 120000)
flash_delay = Config.get_config_value("flash_delay", 120000)
def display():
    global root, title_var, summary_var, link_var, scrolling_summary, timestamp_var, warning_var
    global current_warning, current_fact_var, warning_title_var
    global display_flash
    global refresh_button, fullscreen_button, browser_button

    if Config.get_config_bool("show_display"):

        root = tk.Tk()
        root.title(prog)
        root.configure(bg="black")
        root.geometry("800x600")

        # Fullscreen keybindings
        root.bind("<F11>", ScreenState.toggle_fullscreen)
        root.bind("<Escape>", ScreenState.exit_fullscreen)
        root.bind("<F5>", WeatherFunctions.refresh_weather)
        root.bind("<F6>", CommandWindow.create_command_window)
        root.bind("<F4>", lambda event: browser_helper.WebOpen.opener(port))
        root.bind("<F2>", radar_helper.open_radar)
        # root.bind("<F8>", open_widget)

        # Create StringVar variables
        title_var = tk.StringVar(value=current_title)
        link_var = tk.StringVar(value=current_link)
        warning_var = tk.StringVar(value=warning_summary)
        warning_title_var = tk.StringVar(value=warning_title)
        # current_fact_var = tk.StringVar(value=current_fact)

        # Create and pack labels
        title_label = tk.Label(root, textvariable=title_var, fg="lime", bg="black",
                            font=("VCR OSD Mono", 16, "bold"), justify="left",
                            padx=10, pady=10, wraplength=750)
        title_label.pack()

        # Create scrolling summary (replaces the old summary_label)
        if Config.get_config_bool("show_scroller"):
            scrolling_summary = ScrollingSummary(root, current_summary, width=80, speed=150)

        if Config.get_config_bool("show_link"):
            logging.info("Showing link")
            link_label = tk.Label(
                root, textvariable=link_var,
                fg="cyan", bg="black",
                font=("VCR OSD Mono", 10), justify="left",
                padx=10, pady=10
            )
            link_label.pack()
        else:
            logging.info("Not showing link")

        version_label = tk.Label(
            root, text=current_version,
            fg="cyan", bg="black",
            font=("Courier", 10), justify="left"
        )
        version_label.pack(side=tk.BOTTOM, pady=10, padx=10)

        designed_by_label = tk.Label(
            root, text=designed_by,
            fg="cyan", bg="black",
            font=("Courier", 10), justify="left"
        )
        designed_by_label.pack(side=tk.BOTTOM, pady=10, padx=10)

        if Config.get_config_bool("show_warning"):
            logging.info("Showing warning labels")
            show_warnings = True
            current_warning_title = tk.Label(
                root, textvariable=warning_title_var,
                fg="lime", bg="black",
                font=("VCR OSD Mono", 16, "bold"), justify="left",
                padx=10, pady=10, wraplength=750
            )
            current_warning_title.pack()

            current_warning = tk.Label(
                root, textvariable=warning_var,
                fg="lime", bg="black",
                font=("VCR OSD Mono", 16, "bold"), justify="left",
                padx=10, pady=10, wraplength=750
            )
            current_warning.pack()
        else:
            logging.info("Not showing warning labels")
            show_warnings = False

        # fact_label = tk.Label(root, textvariable=current_fact_var, fg="lime", bg="black",
        #                 font=("VCR OSD Mono", 16, "bold"), justify="left",
        #                 padx=10, pady=10, wraplength=750)

        # fact_label.pack()
        logging.info("Not showing buttons")
        show_buttons = False

        # Add timestamp
        timestamp_var = tk.StringVar()
        timestamp_label = tk.Label(
            root, textvariable=timestamp_var,
            fg="yellow", bg="black",
            font=("Courier", 10)
        )
        timestamp_label.pack(side=tk.BOTTOM, pady=10)

        def update_timestamp():
            timestamp_var.set(f"Current time is {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            root.after(1000, update_timestamp)  # Update every second

        update_timestamp()

        # Set up automatic refresh every 2 minutes
        def auto_refresh():
            WeatherFunctions.refresh_weather()
            timestamp_var.set(f"Auto-refreshed: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            root.after(refresh_delay, auto_refresh)  # 120000 ms = 2 minutes

        def display_flash():
            title_label.config(fg="black")
            link_label.config(fg="black")
            if Config.get_config_bool("show_scroller"):
                scrolling_summary.flash_black()  # Flash the scrolling summary
            timestamp_label.config(fg="black")
            if show_buttons:
                refresh_button.config(bg="black", fg="black", bd=0, highlightthickness=0)
                fullscreen_button.config(bg="black", fg="black", bd=0, highlightthickness=0)
                browser_button.config(fg="black", bg="black", bd=0, highlightthickness=0)
            link_label.config(fg="black")
            if show_warnings:
                current_warning.config(fg="black")
                current_warning_title.config(fg="black")
            version_label.config(fg="black", bg="black")
            designed_by_label.config(fg="black", bg="black")
            # fact_label.config(fg="black")

            # Use after() instead of sleep
            root.after(750, restore_colors)

        def restore_colors():
            title_label.config(fg="lime")
            link_label.config(fg="cyan")
            timestamp_label.config(fg="yellow")
            if show_buttons:
                refresh_button.config(bg="green", fg="yellow", bd=1, highlightthickness=1)
                fullscreen_button.config(bg="blue", fg="white", bd=1, highlightthickness=1)
                browser_button.config(bg="blue", fg="white", bd=1, highlightthickness=1)
            link_label.config(fg="cyan")
            if show_warnings:
                current_warning.config(fg="lime")
                current_warning_title.config(fg="lime")
            version_label.config(fg="cyan", bg="black")
            designed_by_label.config(fg="cyan", bg="black")
            # fact_label.config(fg="lime")

        if Config.get_config_bool("show_cmd"):
            logging.info("Showing command window")
            CommandWindow.create_command_window()
        else:
            logging.info("Not showing command window")

        # Schedule flashes every 10 minutes
        def schedule_flash():
            display_flash()
            root.after(600000, schedule_flash)  # 10 minutes

        # Start the flash cycle
        root.after(600000, schedule_flash)

        root.after(120000, auto_refresh)  # Start auto-refresh after 2 minutes

        weathermodechoice()

        root.mainloop()

class CommandWindow:
    """Static-style class for command window functions"""

    @staticmethod
    def show_help():
        """Open a help window showing contents of txt/help.txt"""
        try:
            with open("txt/help.txt", "r") as helpfile:
                help_text = helpfile.read()
        except FileNotFoundError:
            help_text = "Help file not found!"

        help_window = tk.Toplevel(root)
        help_window.title("Help")
        help_window.geometry("400x300")

        text_widget = tk.Text(help_window, wrap=tk.WORD)
        text_widget.insert(1.0, help_text)
        text_widget.pack(fill=tk.BOTH, expand=True)

    @staticmethod
    def create_command_window(event=None):
        """Create the main command window with buttons"""
        if not root or not root.winfo_exists():
            print("Main window has been destroyed!")
            return None

        cmd_window = tk.Toplevel(root)
        cmd_window.title(f"{prog} Commands")
        cmd_window.geometry("")

        # Help button
        help_btn = tk.Button(
            cmd_window, text="Help",
            command=CommandWindow.show_help
        )
        help_btn.pack(pady=5)

        logging.info("Showing buttons")
        refresh_button = tk.Button(
            cmd_window, text="Refresh Weather (F5)",
            command=WeatherFunctions.refresh_weather,
            bg="green", fg="yellow", font=("VCR OSD Mono", 12)
        )
        refresh_button.pack(pady=10)

        fullscreen_button = tk.Button(
            cmd_window, text="Toggle Fullscreen (F11)",
            command=ScreenState.toggle_fullscreen,
            bg="blue", fg="white", font=("VCR OSD Mono", 12)
        )
        fullscreen_button.pack(pady=5)

        browser_button = tk.Button(
            cmd_window, text="Open webserver page (F4)",
            command=lambda: browser_helper.WebOpen.opener(port),
            bg="blue", fg="white", font=("VCR OSD Mono", 12)
        )
        browser_button.pack(pady=5)

        # widget_button = tk.Button(
        #     cmd_window, text="Open widget mode (F8)",
        #     command=open_widget,
        #     bg="blue", fg="white", font=("VCR OSD Mono", 12)
        # )
        # widget_button.pack(pady=5)

        # forecast_button = tk.Button(cmd_window, text="5 Day Forecast", command=process_weather_entries,
        #                     bg="blue", fg="white", font=("VCR OSD Mono", 12))
        # forecast_button.pack(pady=5)

        radar_button = tk.Button(
            cmd_window, text="Open radar (F2)",
            command=radar_helper.open_radar,
            bg="blue", fg="white", font=("VCR OSD Mono", 12)
        )
        radar_button.pack(pady=5)

        # Exit button
        exit_btn = tk.Button(cmd_window, text="Exit", command=root.quit)
        exit_btn.pack(pady=5)

        # widget_button = tk.Button(
        #     cmd_window, text="Open widget mode (F8)",
        #     command=open_widget,
        #     bg="blue", fg="white", font=("VCR OSD Mono", 12)
        # )
        # widget_button.pack(pady=5)

        return cmd_window


if getattr(sys, 'frozen', False):  # running as exe
    template_folder = os.path.join(sys._MEIPASS, "templates")
    static_folder = os.path.join(sys._MEIPASS, "static")
else:  # running as script
    template_folder = "templates"
    static_folder = "static"

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)

socketio = SocketIO(app, async_mode="threading")

@app.route("/weather")
def webweather():
    logging.info("Flask route accessed!")
    css_url = url_for('static', filename='styles.css')
    try:
        last_updated_value = timestamp_var.get()
    except Exception:
        last_updated_value = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return render_template(
        "weather.html",
        css_url=css_url,
        current_title=current_title,
        current_summary=current_summary,
        warning_title=warning_title,
        warning_summary=warning_summary,
        last_updated=last_updated_value
    )

@app.route("/shutdown", methods=["GET", "POST"])
def shutdown():
    if request.remote_addr != "127.0.0.1":
        return "Forbidden", 403

    # Schedule shutdown after response is sent
    threading.Timer(1.0, lambda: os.kill(os.getpid(), signal.SIGTERM)).start()

    return "Server is shutting down..."

def start_webserver():
    if Config.get_config_bool("webserver"):
        def run_server():
            app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
        threading.Thread(target=run_server, daemon=True).start()
    else:
        logging.info("Not starting webserver")

start_webserver()

# --- Fetch weather data for webserver globals before starting GUI ---
def fetch_initial_weather_globals():
    global current_title, current_summary, current_link, warning_title, warning_summary
    try:
        response = http_get(source_helper.RSS_URL)
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
        logging.error(f"Could not fetch initial weather: {e}")

def dlhistory():
    url = source_helper.RSS_URL
    filename = "history/weatherpegsource.xml"

    # If file exists, append a number
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    # Ensure directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    while os.path.exists(new_filename):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1

    response = http_get(url, stream=True)
    with open(new_filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    logging.info(f"Download complete! Saved as {new_filename}")

# def open_widget(event=None):
#     try:
#         exe_path = os.path.join(os.path.dirname(sys.executable), "weather-widget.exe")
#         subprocess.Popen([exe_path])
#         sys.exit()
#     except FileNotFoundError:
#         subprocess.Popen(["python", "weatherwidget.py"])
#         sys.exit()

def threading_warning_notif(event=None):
    threading.Thread(target=warning_notif, daemon=True).start()

def warning_notif(event=None):
    if os.name == "nt":
        toast("Weather Warning!", "WeatherPeg has detected a potential weather warning or watch!")
    else:
        logging.info("Not doing toast, not on")

if __name__ == "__main__":
    print(f"Welcome to {prog}, version {current_version}")
    logging.info("Fetching initial weather data for webserver...")
    fetch_initial_weather_globals()
    if Config.get_config_bool("show_display"):
        print("Starting GUI...")
        display()
    else:
        logging.info("Not showing display")
        while True:
            time.sleep(1)