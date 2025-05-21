import atexit
import os
import time
import schedule
from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO
import queue
from conscious_assistant import set_up_conscious_assistant, conscious_thinker, tear_down_conscious_assistant
import cv2

os.environ['AGENT_MANIFEST_FILE'] = 'registries/manifest.hocon'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
thread_started = False

user_input_queue = queue.Queue()

conscious_session, conscious_thread = set_up_conscious_assistant()


def conscious_thinking_process():
    with app.app_context():  # Manually push the application context
        global conscious_session, conscious_thread
        thoughts = "thought: hmm, let's see now..."
        while True:
            socketio.sleep(1)

            thoughts, conscious_thread = conscious_thinker(conscious_session, conscious_thread, thoughts)
            print(thoughts)

            # Separating thoughts and speeches
            # Assume 'thoughts' is the string returned by conscious_thinker

            thoughts_to_emit = []
            speeches_to_emit = []

            for line in thoughts.splitlines():
                stripped = line.strip()
                if stripped.startswith("thought:"):
                    # Remove the 'thought:' prefix and strip whitespace
                    content = stripped[len("thought:"):].strip()
                    if content:
                        timestamp = datetime.now().strftime("[%I:%M:%S%p]").lower()
                        thoughts_to_emit.append(f"{timestamp} thought: {content}")
                elif stripped.startswith("say:"):
                    content = stripped[len("say:"):].strip()
                    if content:
                        speeches_to_emit.append(f"{content}")

            # If you want to default any leftover lines to 'thought', add an 'else' block if needed

            # Emitting thoughts and speeches separately
            if thoughts_to_emit:
                socketio.emit('update_thoughts',
                              {'data': '\n'.join(thoughts_to_emit)}, namespace='/chat')
            if speeches_to_emit:
                socketio.emit('update_speech', {'data': '\n'.join(speeches_to_emit)}, namespace='/chat')

            timestamp = datetime.now().strftime("[%I:%M:%S%p]").lower()
            thoughts = f"\n{timestamp} user: " + "[Silence]"
            try:
                user_input = user_input_queue.get(timeout=0.1)
                if user_input:
                    thoughts = f"\n{timestamp} user: " + user_input
                if user_input == "exit":
                    break
            except queue.Empty:
                time.sleep(0.1)
                continue


@socketio.on('connect', namespace='/chat')
def on_connect():
    global thread_started
    if not thread_started:
        thread_started = True
        # let socketio manage the green-thread
        socketio.start_background_task(conscious_thinking_process)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('user_input', namespace='/chat')
def handle_user_input(json, *_):
    user_input = json['data']
    user_input_queue.put(user_input)
    socketio.emit('update_user_input', {'data': user_input}, namespace='/chat')


def cleanup():
    print("Bye!")
    tear_down_conscious_assistant(conscious_session)
    socketio.stop()


@app.route('/shutdown')
def shutdown():
    cleanup()
    cv2.destroyAllWindows()
    return "Capture ended"


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response


def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)


# Register the cleanup function
atexit.register(cleanup)

if __name__ == '__main__':
    socketio.run(app, debug=False, port=5001, allow_unsafe_werkzeug=True, log_output=True, use_reloader=False)
