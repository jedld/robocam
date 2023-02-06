import queue
from typing import Tuple
import camera
import os
import maestro
import utils
import servo_config

class Dummy:
    def __init__(self):
        self.target = {}
        self.range = {}
        return None

    def setAccel(self, channel, value):
        print(f"acceleration set {channel}: {value}")
    
    def setSpeed(self, channel, value):
        print(f"speed set {channel}: {value}")

    def setTarget(self, channel, value):
        print(f"target {channel}: {value}")
        self.target[channel] = value

    def getPosition(self, channel):
        return self.target.get(channel, 0)

    def setRange(self, channel, min, max):
        self.range[channel] = [min, max]

    def getMin(self, channel):
        min, _ = self.range.get(channel, [3000, 9000])
        return min

    def getMax(self, channel):
        _, max = self.range.get(channel, [3000, 9000])
        return max

    def getMovingState(self):
        return False

    def isMoving(self, channel):
        return False

IMAGE_CAPTURE_QUEUE = queue.Queue()
if os.environ.get("TEST"):
    servo = Dummy()
else:
    servo = maestro.Controller('/dev/ttyAMA0')

for s in servo_config.SERVO_CONFIG:
    servo.setRange(s["channel"], 4000, 8000)
    servo.setAccel(s["channel"], 25)
    servo.setSpeed(s["channel"], 20)
    servo.setTarget(s["channel"], 6000)

class JobStatus:
  def __init__(self):
    self.done = False
    self.result = None

def get_servo():
  return servo

def enqueue_image_job(index):
  jobstatus = JobStatus()
  IMAGE_CAPTURE_QUEUE.put(("image", index, jobstatus))
  return jobstatus

def enqueue_motion_job(channel, target):
  jobstatus = JobStatus()
  IMAGE_CAPTURE_QUEUE.put(("motion", [channel, target], jobstatus))
  return jobstatus

def enqueue_wait():
  jobstatus = JobStatus()
  IMAGE_CAPTURE_QUEUE.put(("wait", [], jobstatus))
  return jobstatus

def image_capture_worker():
  print("Image Capture Worker Started")
  while True:
    task, item, jobstatus = IMAGE_CAPTURE_QUEUE.get()
    if task == "image":
      print(f"processing image job {item}")
      fname = camera.capture_image(item)
      jobstatus.done = True
      jobstatus.result = fname
    elif task == "motion":
      print(f"processing motion job {item}")
      servo.setTarget(int(item[0]), int(item[1]))
    elif task == "wait":
      positions = utils.get_current_position(servo)
      jobstatus.done = True
      jobstatus.result = positions