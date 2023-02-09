import os
import time
from PIL import Image, ImageOps

if os.environ.get('TEST'):
  class Picamera2:
    def configure(self, config):
      return None
    def create_still_configuration(self):
      return {}
    def start(self, show_preview=False):
      return None
    def start_and_capture_file(self, fname):
      return None
    def stop(self):
      return None
    def autofocus_cycle(self):
      return True
else:
  from picamera2 import Picamera2

picam2 = Picamera2()
capture_config = picam2.create_still_configuration()
picam2.configure(capture_config)

def capture_image(index = 0, doFlip = False):
  picam2.start(show_preview=False)
  picam2.autofocus_cycle()

  target_filename = f"/tmp/current_{index}.jpg"

  if (os.path.exists(target_filename)):
    destination_directory = os.environ.get("OUTPUT",f"captures/captures_{index}")
    if not os.path.exists(destination_directory):
      os.makedirs(destination_directory, exist_ok=True)
    os.rename(target_filename, os.path.join(destination_directory, f"{int(time.time())}_{os.path.basename(target_filename)}"))
  fname = f"/captures/current_{index}.jpg"
  picam2.start_and_capture_file(fname)
  if doFlip:
    img = Image.open(fname, 'rw')
    flippedImage = ImageOps.flip(img)
    flippedImage.save(fname)
  picam2.stop()
  if os.environ.get('TEST'):
    return 'sample.jpg'
  else:
    return fname