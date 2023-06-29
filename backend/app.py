from flask import Flask, request, jsonify
from flask_cors import CORS
import json, time
import datetime
from typing import Dict, Any
import os
app = Flask(__name__)
CORS(app)

tasks = {
    "I'm on a break": {
        "name": "I'm on a break",
        "time": 0,
        "active": False,
        "start_time": None
    }
}

current_task = "I'm on a break"

@app.route('/')
def index():
    with open('tasks.json', 'r') as f:
        tasks = json.load(f)
    return jsonify(tasks)

@app.route('/tasks', methods=['POST'])
def create_task():
    if request.json is not None:
        task_name = request.json.get('name')
        tasks[task_name] = {
            "name": task_name,
            "time": 0,
            "active": False,
            "start_time": time.time()
        }
        write_tasks_to_file()
        return jsonify(tasks[task_name])
    else:
        return jsonify({"error": "No JSON payload provided"})

@app.route('/tasks/<task_name>/start', methods=['POST'])
def start_task(task_name: str) -> Dict[str, Any]:
    global current_task
    if current_task != task_name:
        if tasks[current_task]["active"]:
            tasks[current_task]["time"] += time.time() - tasks[current_task]["start_time"]
        tasks[current_task]["active"] = False
        current_task = task_name
        tasks[current_task]["start_time"] = time.time()
        tasks[current_task]["active"] = True
        write_tasks_to_file()
    return tasks[current_task]

def write_tasks_to_file():
    data_folder = 'data'
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    today = datetime.datetime.now().strftime('%y%m%d')
    filename = f'{data_folder}/tasks{today}.json'
    if not os.path.exists(filename):
        tasks = {
            "I'm on a break": {
                "name": "I'm on a break",
                "time": 0,
                "active": False,
                "start_time": time.time()
            }
        }
        with open(filename, 'w') as f:
            json.dump(tasks, f)
    else:
        with open(filename, 'r') as f:
            tasks = json.load(f)
    with open(filename, 'w') as f:
        json.dump(tasks, f)

def set_start_time():
    global tasks
    for task in tasks.values():
        if task["start_time"] is None:
            task["start_time"] = time.time()

set_start_time()

if __name__ == '__main__':
    app.run(debug=True)        