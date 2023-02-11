from flask import Flask
import json
import maestro
import time
from flask import request
from flask import render_template
from kinematics import Kinematics
import os
import sqlite3
import utils
import time
import io
import base64
import _thread
import servo_config
import image_capture_worker
from PIL import Image
from flask import send_file
from kinematic_model import EEZYbotARM_Mk2

_thread.start_new_thread(image_capture_worker.image_capture_worker, ())

myRobotArm = EEZYbotARM_Mk2(initial_q1=0, initial_q2=0, initial_q3=0)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

app = Flask(__name__)
servo = image_capture_worker.get_servo()

@app.route("/")
def index():
    conn = get_db_connection()
    bookmarks = conn.execute('SELECT * FROM bookmarks').fetchall()
    conn.close()

    positions = []
    labels = []
    for s in servo_config.SERVO_CONFIG:
        positions.append((s["channel"], s["label"], [servo.getPosition(s["channel"]), servo.getMin(s["channel"]), servo.getMax(s["channel"])]))
    return render_template('index.html', positions=positions, bookmarks = bookmarks, random_number = time.time_ns())

@app.route("/stop", methods=['POST'])
def stop():
    for s in servo_config.SERVO_CONFIG:
        servo.shutoff(s["channel"])
    image_capture_worker.clear()
    return "OK"

@app.route("/set/<id>", methods=['POST'])
def set(id):
    conn = get_db_connection()
    bookmarks = conn.execute('SELECT * FROM bookmarks WHERE id = ?', [id]).fetchall()
    conn.close()
    bookmark = bookmarks[0]
    retract = bookmark['retract']
    moves = json.loads(bookmark['content'])
    image_status_position = None
    servo_status_position = None
    image_capture_worker.enqueue_start()
    for m in moves:
        servo_status_position =image_capture_worker.enqueue_motion_job(m['channel'], m['target'])
    image_status_position =image_capture_worker.enqueue_image_job(bookmark['id'])
    image_capture_worker.enqueue_stop()
    while not image_status_position.done:
        time.sleep(1)
    if retract == 1:
        servo_status_position = utils.enqueue_retract(image_capture_worker)
    return json.dumps(servo_status_position.result)

# loop through all bookmarks and refresh them
@app.route("/refresh_all", methods=['POST'])
def refresh_all():
    conn = get_db_connection()
    bookmarks = conn.execute('SELECT * FROM bookmarks').fetchall()
    conn.close()
    image_status_position = None
    image_capture_worker.enqueue_start()
    for bookmark in bookmarks:
        moves = json.loads(bookmark['content'])
        for m in moves:
            image_capture_worker.enqueue_motion_job(m['channel'], m['target'])
        image_capture_worker.enqueue_wait()
        image_capture_worker.enqueue_image_job(bookmark['id'])
        if bookmark['retract'] == 1:
            final_servo_position = utils.enqueue_retract(image_capture_worker)
   
    # stow arm out of the way
    image_capture_worker.enqueue_stop()
    final_servo_position = utils.enqueue_stow(image_capture_worker)
    while not final_servo_position.done:
        print("blocking until all jobs are done")
        time.sleep(1)

    return json.dumps(final_servo_position.result)
        
@app.route("/delete/<id>", methods=['POST'])
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM bookmarks WHERE id = ?', [id])
    conn.commit()
    bookmarks = conn.execute('SELECT * FROM bookmarks').fetchall()
    conn.close()
    return render_template('bookmarks.html', bookmarks = bookmarks)

@app.route("/save", methods=['POST'])
def save():
    label = request.form['label']
    move_list = request.form['move_list']
    retract_form = request.form.get('retract', 'false')
    if retract_form == 'true':
        retract = 1
    else:
        retract = 0

    conn = get_db_connection()
    conn.execute('INSERT INTO bookmarks (label, content, retract) VALUES (?, ?, ?)', (label, move_list, retract))
    conn.commit()
    bookmarks = conn.execute('SELECT * FROM bookmarks').fetchall()
    conn.close()
    return render_template('bookmarks.html', bookmarks = bookmarks)

@app.route("/image/<id>")
def currentImage(id):
    image_capture_worker.enqueue_start()
    future = image_capture_worker.enqueue_image_job(id)
    image_capture_worker.enqueue_stop()
    while not future.done:
        time.sleep(1)
    print("future done")
    img = Image.open(future.result, mode='r')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    my_encoded_img = base64.encodebytes(img_byte_arr.getvalue()).decode('ascii')
    return my_encoded_img

@app.route("/cached_image/<id>")
def cachedImage(id):
    captures_directory = os.environ.get("OUTPUT",f"captures")
    return send_file(os.path.join(captures_directory, f"current_{id}.jpg"), mimetype='image/jpg')

@app.route("/cached_image_js/<id>")
def cachedImageJs(id):
    captures_directory = os.environ.get("OUTPUT",f"captures")
    img = Image.open(os.path.join(captures_directory, f"current_{id}.jpg"), mode='r')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    my_encoded_img = base64.encodebytes(img_byte_arr.getvalue()).decode('ascii')
    return my_encoded_img


@app.route('/current_xy', methods= ['POST', 'GET'])
def current_xy():
    positions = utils.get_current_position(servo)
    q1 = ((positions[3] + 3000) / (9000-3000)) * 90
    q2 = (positions[1] + 3000) / (9000 - 3000) * 180
    q3 = (positions[2] + 3000) / (9000 - 3000) * 180
    return [q1, q2, q3]

# @app.route("/xycoord", methods=['POST', 'GET'])
# def xycoord():
#     move_list = request.form['move_list']
#     moves = json.loads(move_list)
#     response = []
#     for m in moves:
#         if 'sleep' in m:
#             time.sleep(int(m['sleep']))
#         else:
#             x =  int(m.get('x', 0))
#             y = int(m.get('y', 0))
#             accel = int(m.get('accel', 0))
#             speed = int(m.get('speed', 30))
#             kinematics = Kinematics()
#             arm_a, arm_b = kinematics.move(x, y)
#             angle_a =  int((9000-3000) * ((arm_a + 90) / 180) + 3000)
#             angle_b =  int((9000-3000) * ((arm_b + 90) / 180) + 3000)
#             servo.setAccel(2, accel)
#             servo.setSpeed(2, speed)
#             servo.setTarget(2, angle_a)

#             servo.setAccel(3, accel)
#             servo.setSpeed(3, speed)
#             servo.setTarget(3, angle_b)

#             response.append([angle_a, angle_b, arm_a, arm_b])
#     return json.dumps(response)

@app.route("/stow", methods=['POST'])
def stow():
    servo_status_position = utils.enqueue_stow(image_capture_worker)
    while not servo_status_position.done:
        print("blocking until all jobs are done")
        time.sleep(1)
    final_servo_position = servo_status_position.result
    return json.dumps(final_servo_position)

@app.route("/motion", methods=['POST', 'GET'])
def motion():
    move_list = request.form['move_list']
    moves = json.loads(move_list)
    for m in moves:
        image_capture_worker.enqueue_motion_job(m['channel'], m['target'])
    servo_status_position = image_capture_worker.enqueue_wait()
    while not servo_status_position.done:
        print("blocking until all jobs are done")
        time.sleep(1)
    final_servo_position = servo_status_position.result
    return json.dumps(final_servo_position)

@app.route("/servo/<int:channel>/<int:target>", methods=['POST'])
def move_servo(channel, target):
    if (servo.getMin(channel) <= target and target <= servo.getMax(channel)):
        servo.setTarget(channel, int(target))

        # sleep while servo is still moving
        max_timeout = 30
        while (servo.isMoving(channel) and max_timeout > 0):
            time.sleep(1)
            max_timeout -= 1

    return str(servo.getPosition(channel))

