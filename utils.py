import time
import servo_config
import json
from kinematic_model import EEZYbotARM_Mk2

def enqueue_stow(worker):
    for s in servo_config.SERVO_CONFIG:
        worker.enqueue_motion_job(s['channel'], s['stow'])
    return worker.enqueue_wait()

def enqueue_retract(worker):
    worker.enqueue_motion_job(2, 3698)
    return worker.enqueue_wait()

def get_current_position(servo, max_timeout = 30):
    positions = []

    # sleep while servo is still moving
    for s in servo_config.SERVO_CONFIG:
      while (servo.isMoving(s["channel"]) and max_timeout > 0):
          time.sleep(1)
          max_timeout -= 1

    for s in servo_config.SERVO_CONFIG:
        positions.append((s["channel"],servo.getPosition(s["channel"])))
    return positions


def get_cartesian(kinematics, servo):
    positions = get_current_position(servo)
    q1 = ((positions[2][1] - 3000) / (9000 - 3000)) * 90 - 45
    q2 = ((positions[3][1] - 3000) / (9000 - 3000)) * 180
    q3 = ((positions[4][1] - 3000) / (9000 - 3000)) * 180

    # Compute forward kinematics
    x, y, z = kinematics.forwardKinematics(q1=q1, q2=q2, q3=q3)

    return positions, [x, y, z]