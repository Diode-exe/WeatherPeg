import asyncio
from env_canada import ECRadar
from PIL import Image
import os
import source_helper

async def fetch_radar():
    radar = ECRadar(coordinates=(source_helper.coordinates))
    latest_png = await radar.get_latest_frame()

    filename = "images/radar_img.png"
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename

    # Find a unique filename
    while os.path.exists(new_filename):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1

    # Write the radar image
    with open(new_filename, "wb") as f:
        f.write(latest_png)

    return new_filename  # return the actual filename

def open_radar(event=None):
    # Run async function and get filename
    new_filename = asyncio.run(fetch_radar())

    # Open and show image
    img = Image.open(new_filename)
    img.show()
