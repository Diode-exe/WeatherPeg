import tkinter as tk
import logging
import browser_helper
import radar_helper

class CommandWindow:
    """Static-style class for command window functions"""

    @staticmethod
    def show_help(root_window):
        """Open a help window showing contents of txt/help.txt"""
        try:
            with open("txt/help.txt", "r", encoding="utf-8") as helpfile:
                help_text = helpfile.read()
        except FileNotFoundError:
            help_text = "Help file not found!"

        help_window = tk.Toplevel(root_window)
        help_window.title("Help")
        help_window.geometry("400x300")

        text_widget = tk.Text(help_window, wrap=tk.WORD)
        text_widget.insert(1.0, help_text)
        text_widget.pack(fill=tk.BOTH, expand=True)

    @staticmethod
    def create_command_window(root_window, prog_name, port_num, refresh_func=None, fullscreen_func=None, event=None):
        """Create the main command window with buttons"""
        if not root_window or not root_window.winfo_exists():
            print("Main window has been destroyed!")
            return None

        cmd_window = tk.Toplevel(root_window)
        cmd_window.title(f"{prog_name} Commands")
        cmd_window.geometry("")

        # Help button
        help_btn = tk.Button(
            cmd_window, text="Help",
            command=lambda: CommandWindow.show_help(root_window)
        )
        help_btn.pack(pady=5)

        logging.info("Showing buttons")

        # Refresh button (only if refresh function is provided)
        if refresh_func:
            refresh_button = tk.Button(
                cmd_window, text="Refresh Weather (F5)",
                command=refresh_func,
                bg="green", fg="yellow", font=("VCR OSD Mono", 12)
            )
            refresh_button.pack(pady=10)

        # Fullscreen button (only if fullscreen function is provided)
        if fullscreen_func:
            fullscreen_button = tk.Button(
                cmd_window, text="Toggle Fullscreen (F11)",
                command=fullscreen_func,
                bg="blue", fg="white", font=("VCR OSD Mono", 12)
            )
            fullscreen_button.pack(pady=5)

        # Browser button
        browser_button = tk.Button(
            cmd_window, text="Open webserver page (F4)",
            command=lambda: browser_helper.WebOpen.opener(port_num),
            bg="blue", fg="white", font=("VCR OSD Mono", 12)
        )
        browser_button.pack(pady=5)

        # Radar button
        radar_button = tk.Button(
            cmd_window, text="Open radar (F2)",
            command=radar_helper.open_radar,
            bg="blue", fg="white", font=("VCR OSD Mono", 12)
        )
        radar_button.pack(pady=5)

        # Exit button
        exit_btn = tk.Button(cmd_window, text="Exit", command=root_window.quit)
        exit_btn.pack(pady=5)

        return cmd_window
