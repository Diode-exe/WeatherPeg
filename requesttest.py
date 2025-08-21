import requests

source = "source.txt"
try:
    with open(source, "r") as RSS:
        RSS_URL = RSS.read().strip()
    
    # Debug output
    print(f"Raw URL: {repr(RSS_URL)}")  # This shows hidden characters
    print(f"URL length: {len(RSS_URL)}")
    print(f"Is empty: {RSS_URL == ''}")
    
    if not RSS_URL:
        print("ERROR: URL is empty!")
    else:
        print("Making request...")
        response = requests.get(RSS_URL)
        print(f"Success! Status code: {response.status_code}")
        
except FileNotFoundError:
    print(f"{source} not found!")
except Exception as e:
    print(f"Error: {e}")