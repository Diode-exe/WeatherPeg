source = "txt/source.txt"
try:
    with open(source, "r") as RSS:
        RSS_URL = RSS.read()
except FileNotFoundError:
    print(f"[WARN] {source} not found!")
    print("You need a file called source.txt with a URL pointing towards an XML file so the software knows")
    print("where to get the information from!!")
    input("Press Enter to exit...")