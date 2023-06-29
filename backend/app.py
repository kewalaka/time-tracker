from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import json, time
from datetime import datetime
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

@app.route('/tasks', methods=['GET'])
def get_tasks() -> Dict[str, Any]:
    tasks_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', f'tasks{datetime.now().strftime("%y%m%d")}.json')
    if os.path.exists(tasks_file_path):
        with open(tasks_file_path, 'r') as f:
            tasks = json.load(f)
    else:
        tasks = {}
        for task_name in tasks:
            tasks[task_name] = {
                'name': task_name,
                'active': False,
                'time': 0
            }
        with open(tasks_file_path, 'w') as f:
            json.dump(tasks, f)
    print(tasks)
    return tasks

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
        write_tasks_to_file(tasks)
        return jsonify(tasks[task_name])
    else:
        return jsonify({"error": "No JSON payload provided"})

@app.route('/tasks/<task_name>/start', methods=['POST'])
def start_task(task_name: str) -> Dict[str, Any]:
    global current_task
    if task_name not in tasks:
        return make_response(jsonify({'error': 'Task not found'}), 404)
    if current_task != task_name:
        if tasks[current_task]["active"]:
            tasks[current_task]["time"] += time.time() - tasks[current_task]["start_time"]
        tasks[current_task]["active"] = False
        current_task = task_name
        tasks[current_task]["start_time"] = time.time()
        tasks[current_task]["active"] = True
        write_tasks_to_file(tasks)
    return tasks[current_task]

@app.route('/tasks/<task_name>/stop', methods=['POST'])
def stop_task(task_name: str) -> Dict[str, Any]:
    global current_task
    if task_name not in tasks:
        return make_response(jsonify({'error': 'Task not found'}), 404)
    if current_task == task_name:
        tasks[current_task]["time"] += time.time() - tasks[current_task]["start_time"]
        tasks[current_task]["active"] = False
        current_task = None
        write_tasks_to_file(tasks)
    return tasks[task_name]

def write_tasks_to_file(tasks: Dict[str, Any]) -> None:
    tasks_file_path = os.path.join(os.path.dirname(__file__), '..', 'data', f'tasks{datetime.now().strftime("%y%m%d")}.json')
    if not os.path.exists(tasks_file_path):
        tasks = {
            "I'm on a break": {
                "name": "I'm on a break",
                "time": 0,
                "active": False,
                "start_time": time.time()
            }
        }
        with open(tasks_file_path, 'w') as f:
            json.dump(tasks, f)
    with open(tasks_file_path, 'w') as f:
        json.dump(tasks, f)

if __name__ == '__main__':
    app.run(debug=True)        