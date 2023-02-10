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

def capture_image2(index = 0, doFlip = False):
  picam2.autofocus_cycle()
  captures_directory = os.environ.get("OUTPUT",f"captures")
  if not os.path.exists(captures_directory):
      os.makedirs(captures_directory, exist_ok=True)
  target_filename = os.path.join(captures_directory, f"current_{index}.jpg")

  if (os.path.exists(target_filename)):
    destination_directory = os.path.join(captures_directory, f"captures_{index}")
    if not os.path.exists(destination_directory):
      os.makedirs(destination_directory, exist_ok=True)
    os.rename(target_filename, os.path.join(destination_directory, f"{int(time.time())}_{os.path.basename(target_filename)}"))

  picam2.capture_file(target_filename)
  if doFlip:
    img = Image.open(target_filename, 'r')
    flippedImage = ImageOps.flip(img)
    flippedImage.save(target_filename)

  if os.environ.get('TEST'):
    return 'sample.jpg'
  else:
    return target_filename

def capture_image(index = 0, doFlip = False):
  picam2.start(show_preview=False)
  result = capture_image2(index, doFlip)
  picam2.stop()
  return result
