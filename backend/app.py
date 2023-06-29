from flask import Flask, request, jsonify
from flask_cors import CORS
import json, time

app = Flask(__name__)
CORS(app)

tasks = {
    "I'm on a break": {
        "name": "I'm on a break",
        "time": 0,
        "active": False
    }
}

current_task = "I'm on a break"

def write_tasks_to_file():
    with open('tasks.json', 'w') as f:
        json.dump(tasks, f)

@app.route('/tasks', methods=['POST'])
def create_task():
    if request.json is not None:
        task_name = request.json.get('name')
        tasks[task_name] = {
            "name": task_name,
            "time": 0,
            "active": False
        }
        write_tasks_to_file()
        return jsonify(tasks[task_name])
    else:
        return jsonify({"error": "No JSON payload provided"})

@app.route('/tasks/<task_name>/start', methods=['POST'])
def start_task(task_name):
    global current_task
    if current_task != task_name:
        tasks[current_task]["active"] = False
        current_task = task_name
    tasks[task_name]["active"] = True
    tasks[task_name]["start_time"] = time.time()  # Store the start time
    write_tasks_to_file()
    return jsonify(tasks[task_name])

@app.route('/tasks/<task_name>/stop', methods=['POST'])
def stop_task(task_name):
    task = tasks[task_name]
    if task["active"]:
        elapsed_time = time.time() - task["start_time"]
        task["time"] += elapsed_time  # Update the time attribute
        task["active"] = False
        write_tasks_to_file()
    return jsonify(task)

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(list(tasks.values()))

@app.route('/tasks/<task_name>', methods=['GET'])
def get_task(task_name):
    return jsonify(tasks[task_name])

@app.route('/tasks/<task_name>/time', methods=['GET'])
def get_task_time(task_name):
    return jsonify(tasks[task_name]["time"])

@app.route('/tasks/<task_name>/switch', methods=['POST'])
def switch_task(task_name):
    global current_task
    current_task_obj = tasks[current_task]
    if current_task_obj["active"]:
        elapsed_time = time.time() - current_task_obj["start_time"]
        current_task_obj["time"] += elapsed_time  # Update the time attribute
    current_task_obj["active"] = False
    current_task = task_name
    task = tasks.get(task_name)
    if task is None:
        task = {
            "name": task_name,
            "time": 0,
            "active": True
        }
        tasks[task_name] = task
    else:
        task["active"] = True
    task["start_time"] = time.time()  # Store the start time
    write_tasks_to_file()
    return jsonify(task)

if __name__ == '__main__':
    app.run(debug=True)