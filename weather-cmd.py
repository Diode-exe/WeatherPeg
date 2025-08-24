import requests
import feedparser
import re
import html
import tkinter as tk
import datetime
import os
import tts_helper
import source_helper
import time
import threading

# RSS_URL = "https://weather.gc.ca/rss/city/mb-38_e.xml"
# RSS_URL2 = "https://weather.gc.ca/rss/weather/49.591_-96.89_e.xml"
# Leaving this in just for reference in case I lose the URLs
# Don't use these, it' all handled in source_helper.py

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

global weathermodechoice

current_version = "WeatherPeg Version 1.9.1"
designed_by = "Designed by Diode-exe"

class ScrollingSummary:
    def __init__(self, parent, text="", width=80, speed=150):
        self.original_text = text
        self.width = width
        self.speed = speed
        self.position = 0
        self.is_scrolling = False

        self.label = tk.Label(parent, text="", fg="lime", bg="black",
                            font=("Courier", 12), justify="left",
                            padx=10, pady=10)
        self.label.pack()

        self.update_text(text)

    def update_text(self, new_text):
        self.original_text = new_text
        self.position = 0

        # Only scroll if text is longer than display width
        if len(new_text) <= self.width:
            self.is_scrolling = False
            self.label.config(text=new_text)
        else:
            self.is_scrolling = True
            self.scroll()

    def scroll(self):
        if not self.is_scrolling or not self.original_text:
            return

        # Create extended text with spacing for smooth looping
        extended_text = self.original_text + "   ***   "

        # Calculate visible portion
        start = self.position % len(extended_text)
        display_text = (extended_text[start:] + extended_text)[:self.width]

        self.label.config(text=display_text)

        # Move position for next update
        self.position += 1

        # Schedule next update
        self.label.after(self.speed, self.scroll)

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
        if ScrollingSummary.scrolling_summary:
            ScrollingSummary.scrolling_summary.update_text(current_summary)


class WeatherFunctions():
    # this does not use self, for the record
    def update_forecast():
        title_var.set(current_title)
        scrolling_summary.update_text(current_summary)
        warning_var.set("")
        warning_title_var.set("")

    def refresh_weather(event=None):
        """Refresh weather data and update display"""
        weathermodechoice()
        logger()
        # random_fact()
        # current_fact_var.set(current_fact)
        display_flash()
        update_display()

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

    # def hide_elements():
    #     refresh_button.pack_forget()
    #     fullscreen_button.pack_forget()
    #     instructions.pack_forget()
    #     root.config(cursor="none")

    # def show_elements():
    #     fullscreen_button.pack(pady=5)
    #     refresh_button.pack(pady=10)
    #     instructions.pack(pady=5)
    #     root.config(cursor="")

def logger():
    filename = "txt/history.txt"
    logged_time = timestamp_var.get()
    if os.path.exists(filename):
        print(f"[LOG] Found {filename}")
    else:
        print(f"[LOG] Could not find {filename}, but created it")
    with open(filename, "a") as f:
            f.write(f"{current_title}\n")
            f.write(f"Summary: {current_summary}\n")
            f.write(f"Coords/Link: {current_link}\n")
            f.write(f"Current warning: {warning_summary}\n")
            f.write(f"Logged time: {logged_time}\n")
            f.write("-" * 50 + "\n")
    print(f"[LOG] Logged current weather to {filename}")

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

def main_speaker(text):
    tts_enabled = tts_helper.get_config_bool_tts("do_tts")
    print(f"[LOG] TTS enabled: {tts_enabled}")  # Debug line
    if tts_enabled:
        print(f"[LOG] About to speak: {text}")  # Debug line
        tts_helper.speaker(text)
    else:
        print("[LOG] TTS is disabled in config")

def weathermodechoice():
    if get_config_bool("mode"):
        def get_weather():
            # mode 1

            # Fetch fresh data
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
                    title_var.set(current_title)
                    link_var.set(current_link)
                    warning_var.set(warning_summary)
                    warning_title_var.set(warning_title)
                    scrolling_summary.update_text(current_summary)
                    break

            if tts_helper.get_config_bool_tts("do_tts"):
                tts_helper.speaker(current_title)
                tts_helper.speaker(current_summary)
                tts_helper.speaker(warning_title)
                tts_helper.speaker(warning_summary)
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
                        response = requests.get(source_helper.RSS_URL)
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
                            
                            # Update GUI on main thread
                            def update_gui():
                                # Update your StringVars
                                title_var.set(current_title)
                                link_var.set(current_link)
                                warning_var.set(current_summary)
                                warning_title_var.set(current_title)
                                scrolling_summary.update_text(current_summary)
                                
                                update_display()
                            update_gui()

                            if tts_helper.get_config_bool_tts("do_tts"):
                                tts_helper.speaker(current_title)
                                tts_helper.speaker(current_summary)
                            
                            index = (index + 1) % len(weather_entries)
                            
                            # Schedule GUI update on main thread
                            if 'root' in globals() and root:
                                root.after(0, update_gui)
                    except Exception as e:
                        print(f"Error in weather cycle: {e}")
                    
                    time.sleep(30)
            
            thread = threading.Thread(target=background_cycle)
            thread.daemon = True
            thread.start()

        cycle_weather_entries()
pass

def display():
    global root, title_var, summary_var, link_var, scrolling_summary, timestamp_var, warning_var, current_warning, current_fact_var, warning_title_var
    global display_flash
    global refresh_button, fullscreen_button, instructions
    global show_warnings, show_instructions, show_buttons

    root = tk.Tk()
    root.title("WeatherPeg")
    root.configure(bg="black")
    root.geometry("800x600")

    # Fullscreen keybindings
    root.bind("<F11>", ScreenState.toggle_fullscreen)
    root.bind("<Escape>", ScreenState.exit_fullscreen)
    root.bind("<F5>", WeatherFunctions.refresh_weather)
    root.bind("<F6>", CommandWindow.create_command_window)

    # Create StringVar variables
    title_var = tk.StringVar(value=current_title)
    link_var = tk.StringVar(value=current_link)
    warning_var = tk.StringVar(value=warning_summary)
    warning_title_var = tk.StringVar(value=warning_title)
    # current_fact_var = tk.StringVar(value=current_fact)

    # Create and pack labels
    title_label = tk.Label(root, textvariable=title_var, fg="lime", bg="black",
                          font=("Courier", 16, "bold"), justify="left",
                          padx=10, pady=10, wraplength=750)
    title_label.pack()

    # Create scrolling summary (replaces the old summary_label)
    scrolling_summary = ScrollingSummary(root, current_summary, width=80, speed=150)

    if get_config_bool("show_link"):
        print("[LOG] Showing link")
        link_label = tk.Label(
            root, textvariable=link_var, 
            fg="cyan", bg="black",
            font=("Courier", 10), justify="left",
            padx=10, pady=10
        )
        link_label.pack()
    else:
        print("[LOG] Not showing link")

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

    if get_config_bool("show_warning"):
        print("[LOG] Showing warning label")
        show_warnings = True
        current_warning_title = tk.Label(
            root, textvariable=warning_title_var, 
            fg="lime", bg="black",
            font=("Courier", 16, "bold"), justify="left",
            padx=10, pady=10, wraplength=750
        )
        current_warning_title.pack()

        current_warning = tk.Label(
            root, textvariable=warning_var, 
            fg="lime", bg="black",
            font=("Courier", 16, "bold"), justify="left",
            padx=10, pady=10, wraplength=750
        )
        current_warning.pack()
    else:
        print("[LOG] Not showing warning labels")
        show_warnings = False

    # fact_label = tk.Label(root, textvariable=current_fact_var, fg="lime", bg="black",
    #                 font=("Courier", 16, "bold"), justify="left",
    #                 padx=10, pady=10, wraplength=750)

    # fact_label.pack()

    if get_config_bool("show_buttons"):
        print("[LOG] Showing buttons")
        refresh_button = tk.Button(
            root, text="Refresh Weather (F5)", 
            command=WeatherFunctions.refresh_weather,
            bg="green", fg="yellow", font=("Courier", 12)
        )
        refresh_button.pack(pady=10)

        fullscreen_button = tk.Button(
            root, text="Toggle Fullscreen (F11)", 
            command=ScreenState.toggle_fullscreen,
            bg="blue", fg="white", font=("Courier", 12)
        )
        fullscreen_button.pack(pady=5)
        # forecast_button = tk.Button(root, text="5 Day Forecast", command=process_weather_entries,
        #                     bg="blue", fg="white", font=("Courier", 12))
        # forecast_button.pack(pady=5)
        show_buttons = True
    else:
        print("[LOG] Not showing buttons")
        show_buttons = False

    if get_config_bool("show_instruction"):
        print("[LOG] Showing instruction")
        show_instructions = True
        # Add instructions
        instructions = tk.Label(
            root, text="Press F11 to toggle fullscreen • Press Escape to exit fullscreen",
            fg="gray", bg="black",
            font=("Courier", 10)
        )
        instructions.pack(pady=5)
    else:
        print("[LOG] Not showing instruction")
        show_instructions = False

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
        root.after(120000, auto_refresh)  # 120000 ms = 2 minutes

    def display_flash():
        title_label.config(fg="black")
        link_label.config(fg="black")
        scrolling_summary.flash_black()  # Flash the scrolling summary
        if show_instructions:
            instructions.config(fg="black")
        timestamp_label.config(fg="black")
        if show_buttons:
            refresh_button.config(bg="black", fg="black", bd=0, highlightthickness=0)
            fullscreen_button.config(bg="black", fg="black", bd=0, highlightthickness=0)
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
        if show_instructions:
            instructions.config(fg="gray")
        timestamp_label.config(fg="yellow")
        if show_buttons:
            refresh_button.config(bg="green", fg="yellow", bd=1, highlightthickness=1)
            fullscreen_button.config(bg="blue", fg="white", bd=1, highlightthickness=1)
        link_label.config(fg="cyan")
        if show_warnings:
            current_warning.config(fg="lime")
            current_warning_title.config(fg="lime")
        version_label.config(fg="cyan", bg="black")
        designed_by_label.config(fg="cyan", bg="black")
        # fact_label.config(fg="lime")

    if get_config_bool("show_cmd"):
        print("[LOG] Showing command window")
        CommandWindow.create_command_window()
    else:
        print("[LOG] Not showing command window")

    # Schedule flashes every 10 minutes
    def schedule_flash():
        display_flash()
        root.after(600000, schedule_flash)  # 10 minutes

    # Start the flash cycle
    root.after(600000, schedule_flash)

    root.after(120000, auto_refresh)  # Start auto-refresh after 2 minutes

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
        cmd_window.title("WeatherPeg Commands")
        cmd_window.geometry("300x200")
    
        # Help button
        help_btn = tk.Button(
            cmd_window, text="Help", 
            command=CommandWindow.show_help
        )
        help_btn.pack(pady=5)

        # Fullscreen toggle button
        fullscreen_button = tk.Button(
            cmd_window, 
            text="Toggle Fullscreen (F11)", 
            command=ScreenState.toggle_fullscreen,
            bg="blue", fg="white", font=("Courier", 12)
        )
        fullscreen_button.pack(pady=5)

        # Refresh weather button
        refresh_button = tk.Button(
            cmd_window, 
            text="Refresh Weather (F5)", 
            command=WeatherFunctions.refresh_weather,
            bg="green", fg="yellow", font=("Courier", 12)
        )
        refresh_button.pack(pady=10)
    
        # Exit button
        exit_btn = tk.Button(cmd_window, text="Exit", command=root.quit)
        exit_btn.pack(pady=5)
    
        return cmd_window


# Main execution
if __name__ == "__main__":
    print(f"Welcome to WeatherPeg, version {current_version}")
    print("Fetching initial weather data...")
    print("Starting GUI...")
    display()
    weathermodechoice()