import subprocess

def build(spec_file):
    print(f"Building {spec_file}...")
    subprocess.run(["pyinstaller", spec_file], check=True)

if __name__ == "__main__":
    build("WeatherPeg.spec")
    print("Done building")
