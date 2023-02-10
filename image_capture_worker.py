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

    def shutoff(self, channel):
        print(f"target channel shutdown")
        self.target[channel] = 0

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
    servo.setRange(s["channel"], s.get("min", 4000), s.get("max",8000))
    servo.setAccel(s["channel"], 25)
    servo.setSpeed(s["channel"], 20)
    servo.setTarget(s["channel"], 6000)

class JobStatus:
  def __init__(self):
    self.done = False
    self.result = None

def get_servo():
  return servo

def clear():
  with IMAGE_CAPTURE_QUEUE.mutex:
    IMAGE_CAPTURE_QUEUE.queue.clear()

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

def enqueue_start():
  jobstatus = JobStatus()
  IMAGE_CAPTURE_QUEUE.put(("start_cam", [], jobstatus))
  return jobstatus

def enqueue_stop():
  jobstatus = JobStatus()
  IMAGE_CAPTURE_QUEUE.put(("stop_cam", [], jobstatus))
  return jobstatus

def image_capture_worker():
  picam2 = camera.picam2
  print("Image Capture Worker Started")
  while True:
    task, item, jobstatus = IMAGE_CAPTURE_QUEUE.get()
    if task == "start_cam":
      print("Start Camera")
      picam2.start(show_preview=False)
      jobstatus.done = True
      jobstatus.result = None
    elif task == "stop_cam":
      print("Stop Camera")
      picam2.stop()
      jobstatus.done = True
      jobstatus.result = None
    elif task == "image":
      print(f"processing image job {item}")
      positions = utils.get_current_position(servo)

      # check veritical camera position if < 6000 flip the image
      if positions[0][1] < 6000: 
        fname = camera.capture_image2(item, True)
      else:
        fname = camera.capture_image2(item)
      jobstatus.done = True
      jobstatus.result = fname
    elif task == "motion":
      print(f"processing motion job {item}")
      servo.setTarget(int(item[0]), int(item[1]))
    elif task == "wait":
      positions = utils.get_current_position(servo)
      jobstatus.done = True
      jobstatus.result = positions
