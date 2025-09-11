import asyncio
from env_canada import ECRadar
from PIL import Image, ImageSequence
import time

async def fetch_radar():
    # Centered on Winnipeg (example)—adjust lat/lon to your area
    radar = ECRadar(coordinates=(49.8951, -97.1384))  
    animated_gif = await radar.get_loop()         # multi-frame animation
    latest_png = await radar.get_latest_frame()   # single-frame image
    # Save them to disk
    with open("radar.gif", "wb") as f:
        f.write(animated_gif)
    with open("radar_latest.png", "wb") as f:
        f.write(latest_png)

asyncio.run(fetch_radar())
# img = Image.open("radar_latest.png")  # open an image file
# img.show()
gif = Image.open("radar.gif")
for i, frame in enumerate(ImageSequence.Iterator(gif)):
    print(f"Frame {i}: size={frame.size}, mode={frame.mode}")
    frame.show()
    time.sleep(0.1)