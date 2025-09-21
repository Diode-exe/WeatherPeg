import subprocess

def build(spec_file):
    print(f"Building {spec_file}...")
    subprocess.run(["pyinstaller", spec_file], check=True)

if __name__ == "__main__":
    build("WeatherPeg-console.spec")
    print("Console version done building")
    build("WeatherPeg-windowed.spec")
    print("Console-less version done building")
    build("WeatherPeg-widget.spec")
    print("Widget done building")
