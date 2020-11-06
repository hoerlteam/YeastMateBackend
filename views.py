import os
import copy
import json

from flask import render_template
from flask import request, jsonify

from app import app
from tasks import start_pipeline, align_task, detect_task, export_task

from app import huey

import logging
logging.basicConfig(level=logging.DEBUG)

@huey.pre_execute()
def add_execute_task(task):
    global executing_tasks

    tasks = json.loads(huey.storage.peek_data('tasks'))

    if task.name == 'align_task':
        tasks[task.id+'align'] = {'Job': 'Alignment', 'Path': task.args[0], 'Status': 'Running'}

        if task.args[1]:
            tasks[task.id+'detect'] = {'Job': 'Detection', 'Path': task.args[0], 'Status': 'Pending'}

    elif task.name == 'detect_task':
        tasks[task.id+'detect'] = {'Job': 'Detection', 'Path': task.args[0], 'Status': 'Running'}

    else:
        return

    huey.storage.put_data('tasks', json.dumps(tasks).encode('utf-8'))

@huey.post_execute()
def remove_execute_task(task, task_value, exc):
    if task.name != 'start_pipeline':
        tasks = json.loads(huey.storage.peek_data('tasks'))
        try:
            del tasks[task.id+'align']
        except:
            pass

        try:
            del tasks[task.id+'detect']
        except:
            pass

        huey.storage.put_data('tasks', json.dumps(tasks).encode('utf-8'))

@app.route('/', methods=['POST'])
def queue_job():
    align = False
    detect = False
    if 'align' in request.json.keys():
        align = True
    if 'detect' in request.json.keys():
        detect = True

    pipeline = start_pipeline.s(align, detect, request.json['path'])
    
    if 'align' in request.json.keys():
        path = os.path.join(request.json['path'])

        alignment = request.json['align']['alignment']
        channels = request.json['align']['channels'] 
        file_format = request.json['align']['inputFileFormat'] 
        dimensions = request.json['align']['dimensions']

        pipeline = pipeline.then(align_task, path, detect, alignment, channels, file_format, dimensions)

    if 'detect' in request.json.keys():
        path = os.path.join(request.json['path'])

        zstack = request.json['detect']['zstack']
        video = request.json['detect']['video']
        graychannel = request.json['detect']['graychannel']
        boxsize = request.json['detect']['boxsize']
        box_expansion = request.json['detect']['boxExpansion']
        frame_selection = request.json['detect']['frameSelection']
        ip = request.json['detect']['ip']

        pipeline = pipeline.then(detect_task, path, zstack, graychannel, video, frame_selection, box_expansion, boxsize, ip)

    if 'export' in request.json.keys():
        path = os.path.join(request.json['path'])

        pipeline = pipeline.then(export_task, path)

    huey.enqueue(pipeline)

    return 'Queued, success'

@app.route('/', methods=['GET'])
def get_tasklist():
    tasklist = list(json.loads(huey.storage.peek_data('tasks')).values())

    tasks = huey.pending()
    for t in tasks:
        if t.name == 'start_pipeline':
            if t.args[0]:
                job = 'Alignment'
                tasklist.append({'Job': job, 'Path': t.args[3], 'Status': 'Pending'})
            
            if t.args[1]:
                job = 'Detection'
                tasklist.append({'Job': job, 'Path': t.args[3], 'Status': 'Pending'})

        elif t.name == 'align_task':
            job = 'Alignment'
            tasklist.append({'Job': job, 'Path': t.args[0], 'Status': 'Pending'})
            
            if t.args[1]:
                job = 'Detection'
                tasklist.append({'Job': job, 'Path': t.args[0], 'Status': 'Pending'})

        elif t.name == 'detect_task':
            job = 'Detection'
            tasklist.append({'Job': job, 'Path': t.args[0], 'Status': 'Pending'})

        else:
            continue

    return jsonify({'tasks' : tasklist})