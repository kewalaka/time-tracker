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
    global tasks
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
    for task_name in tasks:
        tasks[task_name]['active'] = False
        tasks[task_name]['start_time'] = 0
    write_tasks_to_file(tasks)
    print("Current tasks on load:", tasks)
    return tasks

@app.route('/tasks', methods=['POST'])
def create_task() -> Dict[str, Any]:
    task_name = request.json.get('name')
    if task_name:
        if task_name in tasks:
            return make_response(jsonify({'error': 'Task already exists'}), 400) # type: ignore
        tasks[task_name] = {
            'name': task_name,
            'active': True,
            'time': 0,
            'start_time': time.time() # Initialize start_time to current timestamp
        }
        write_tasks_to_file(tasks)
        return make_response(jsonify(tasks[task_name]), 200) # type: ignore
    else:
        return make_response(jsonify({'error': 'No JSON payload provided'}), 400) # type: ignore

# when the a start request is made, the current task is stopped and the start_time is used to calculate the elapsed time
# the start_time of the new task is set to the current timestamp
# there is no current task when the application first starts
@app.route('/tasks/<task_name>/start', methods=['POST'])
def start_task(task_name: str) -> Dict[str, Any]:
    global current_task
    print("Current task that is active:", current_task)
    print("List of tasks when when /start begins:", tasks)
    if task_name not in tasks:
        return make_response(jsonify({'error': 'Task not found'}), 404)
    if current_task is not None and tasks[current_task]["active"]:
        tasks[current_task]["time"] += time.time() - tasks[current_task]["start_time"]
    if current_task is None:
        current_task = task_name
    else:
        current_task = task_name if current_task != task_name else current_task
    tasks[current_task]["start_time"] = time.time()
    tasks[current_task]["active"] = True
    print("List of tasks when when /start ends:", tasks)
    write_tasks_to_file(tasks)
    return tasks[current_task]

# when a stop request is received, the elapsed time is calculated from start_time and added to the total time
# if start_time is None, the task has not been started yet and the elapsed time is 0
@app.route('/tasks/<task_name>/stop', methods=['POST'])
def stop_task(task_name: str) -> Dict[str, Any]:
    global current_task
    if task_name not in tasks:
        return make_response(jsonify({'error': 'Task not found'}), 404) # type: ignore
    if current_task == task_name:
        if tasks[current_task]["start_time"] is not None:
            elapsed_time = time.time() - tasks[current_task]["start_time"]
            tasks[current_task]["time"] += elapsed_time
        tasks[current_task]["active"] = False
        tasks[current_task]["start_time"] = None
        current_task = None
        write_tasks_to_file(tasks)
    else:
        if tasks[task_name]["start_time"] is not None:
            elapsed_time = time.time() - tasks[task_name]["start_time"]
            tasks[task_name]["time"] += elapsed_time
        tasks[task_name]["active"] = False
        tasks[task_name]["start_time"] = None
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