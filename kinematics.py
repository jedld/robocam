
import math
import time

class CColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class LogType:
    DEBUG = 0
    NORMAL = 1
    WARNING = 2
    ERROR = 3
    NONE = 4

log_level = LogType.NORMAL

def log(message, type=LogType.NORMAL):
    if type >= log_level:
        if type == LogType.NORMAL:
            print(message)
        elif type == LogType.DEBUG:
            print("DEBUG: " + message)
        elif type == LogType.WARNING:
            print(CColors.WARNING + "WARNING: " + message + CColors.ENDC)
        elif type == LogType.ERROR:
            print(CColors.ERROR + "ERROR: " + message + CColors.ENDC)

class Kinematics:
  def __init__(self):
      self.INNER_ARM_LENGTH = 134.5
      self.OUTER_ARM_LENGTH = 210
      self.A_VERTICAL = 0          # a servo angle when wing is vertical
      self.B_VERTICAL = -90          # b servo angle when wing is vertical
      self.A_MIN_FROM_VERTICAL = 80   # a servo minimum degrees from vertical [vert - min]
      self.B_MIN_FROM_VERTICAL = 0 # b servo minimum degrees from vertical [vert - min]
      self.A_MAX_FROM_VERTICAL = 80  # a servo minimum degrees from vertical [vert + max]
      self.B_MAX_FROM_VERTICAL = 170  # b servo minimum degrees from vertical [vert + max]
      
  def distance(self, start_point, end_point):
      """ Returns the distance from the first point to the second """
      return math.sqrt((start_point[0] - end_point[0])**2 + (start_point[1] - end_point[1])**2)

  def law_of_cosines(self, a, b, c):
      """ Performs the Law of Cosines on the given side lengths """
      return math.degrees(math.acos((c**2 - b**2 - a**2)/(-2.0 * a * b)))

  def move(self, x, y):
      """ Returns the angles necessary to reach the given coordinate point """
      # Made with love by Idrees @ https://github.com/IdreesInc
      distance_to_goal = self.distance((0, 0), (x, y))
      if distance_to_goal == 0:
          log("Cannot move to origin", LogType.ERROR)
          return None, None
      angle_from_horizontal = math.degrees(math.asin(y / distance_to_goal))
      try:
          triangle_a = self.law_of_cosines(self.INNER_ARM_LENGTH, distance_to_goal, self.OUTER_ARM_LENGTH)
          triangle_b = self.law_of_cosines(self.INNER_ARM_LENGTH, self.OUTER_ARM_LENGTH, distance_to_goal)
          log("[Triangle] a: %s, b: %s, angle from horiz: %s" % (triangle_a, triangle_b, angle_from_horizontal), LogType.DEBUG)
          servo_angle_a = 90 - triangle_a - angle_from_horizontal
          servo_angle_b = triangle_b - servo_angle_a + angle_from_horizontal
          log("[Servos] a: %s, b: %s" % (servo_angle_a, servo_angle_b), LogType.DEBUG)
          return [self.A_VERTICAL + servo_angle_a, self.B_VERTICAL + servo_angle_b]
      except ValueError:
          log("Coordinates out of range due to the physical laws of the universe (given point is out of reach)", LogType.ERROR)
      return None, None