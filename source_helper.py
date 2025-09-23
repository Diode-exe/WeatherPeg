source = "txt/source.txt"
try:
    with open(source, "r") as RSS:
        RSS_URL = RSS.read()
except FileNotFoundError:
    print(f"[WARN] {source} not found!")
    print("You need a file called source.txt with a URL pointing towards an XML file so the software knows")
    print("where to get the information from!!")
    input("Press Enter to continue...")

coord_source = "txt/coord_source.txt"

try:
    with open(coord_source, "r") as f:
        line = f.read().strip()
        if not line:
            raise ValueError("Coordinate file is empty")
        lat_str, lon_str = line.split(",")
        coordinates = (float(lat_str), float(lon_str))  # ✅ tuple of floats
except FileNotFoundError:
    print(f"[WARN] {coord_source} not found!")
    print("You need a file called coord_source.txt with coords in it so the radar has a location")
    input("Press Enter to continue...")
    coordinates = None
except ValueError as e:
    print(f"[WARN] {coord_source} is invalid: {e}")
    input("Press Enter to continue...")
    coordinates = None

print("Coordinates:", coordinates)
