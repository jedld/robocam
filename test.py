import maestro
import time

servo.setAccel(0,25)
servo.setTarget(0,6000)
servo.setAccel(1,25)
servo.setTarget(1,6000)
time.sleep(2)
servo.setAccel(0,25)
servo.setTarget(0,1000)
servo.setAccel(1,25)
servo.setAccel(1,1000)
time.sleep(2)
servo.setAccel(0,25)
servo.setTarget(0,6000)
servo.setAccel(1,25)
servo.setTarget(1, 6000)
servo.close
