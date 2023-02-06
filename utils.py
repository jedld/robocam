import time
import servo_config

def enqueue_stow(worker):
    for s in servo_config.SERVO_CONFIG:
        worker.enqueue_motion_job(s['channel'], s['stow'])
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