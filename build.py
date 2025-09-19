import PyInstaller.__main__

# Name of your main script
MAIN_SCRIPT = "weather-cmd.py"

def build_console():
    PyInstaller.__main__.run([
        MAIN_SCRIPT,
        "--onefile",
        "--console",
        "--clean",
        "--distpath", "dist/console",   # put console build here
        "--workpath", "build/console",
        "--name", "WeatherPeg-Console"
    ])

def build_windowed():
    PyInstaller.__main__.run([
        MAIN_SCRIPT,
        "--onefile",
        "--noconsole",
        "--clean",
        "--distpath", "dist/windowed",  # put windowed build here
        "--workpath", "build/windowed",
        "--name", "WeatherPeg"
    ])

if __name__ == "__main__":
    print("🔨 Building console version...")
    build_console()
    print("✅ Console version done.")

    print("🔨 Building windowed version...")
    build_windowed()
    print("✅ Windowed version done.")

    print("\n🎉 Both builds finished! Check the dist/ folder.")
