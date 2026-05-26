from flask import Flask, render_template, request, redirect
import json
import os
from datetime import datetime

app = Flask(__name__)

FILE_NAME = 'tasks.json'

def load_tasks():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)

tasks = load_tasks()

@app.route('/search')
def search():
    query = request.args.get('q', '').strip().lower()
    if query:
        filtered_tasks = [task for task in tasks if query in task['text'].lower()]
    else:
        filtered_tasks = tasks
    return render_template('index.html', tasks=filtered_tasks, search_query=query)

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    new_task_text = request.form['task']
    task_priority = request.form.get('priority', 'Обычный')
    
    if new_task_text:
        task = {
            'text': new_task_text,
            'date': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'done': False,
            'priority': task_priority
        }
        tasks.append(task)
        save_tasks(tasks)
    return redirect('/')

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)
        save_tasks(tasks)
    return redirect('/')

@app.route('/clear')
def clear_tasks():
    tasks.clear()
    save_tasks(tasks)
    return redirect('/')

@app.route('/toggle/<int:task_id>')
def toggle_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks[task_id]['done'] = not tasks[task_id]['done']
        save_tasks(tasks)
    return redirect('/')

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    if task_id < 0 or task_id >= len(tasks):
        return "Задача не найдена", 404

    task = tasks[task_id]

    if request.method == 'POST':
        new_text = request.form.get('task', '').strip()

        if new_text == '':
            return render_template(
                'edit.html',
                task=task,
                message="Текст не может быть пустым!"
            )
       
        old_text = task['text']
        if new_text == old_text:
            return render_template(
                'edit.html',
                task=task,
                message="Ничего не изменено"
            )
            
        new_priority = request.form.get('priority', 'Обычный')
        tasks[task_id]['priority'] = new_priority
        
        tasks[task_id]['text'] = new_text
        save_tasks(tasks)
        return redirect('/')

    else:
        return render_template('edit.html', task=task)

@app.route('/active')
def active_tasks():
    active = [task for task in tasks if not task.get('done', False)]
    return render_template('index.html', tasks=active, show_active=True)

@app.route('/completed')
def completed_tasks():
    completed = [task for task in tasks if task.get('done', False)]
    return render_template('index.html', tasks=completed, show_completed=True)

@app.route('/complete-all')
def complete_all():
    for task in tasks:
        task['done'] = True
    save_tasks(tasks)
    return redirect('/')

@app.route('/incomplete-all')
def incomplete_all():
    for task in tasks:
        task['done'] = False
    save_tasks(tasks)
    return redirect('/')

#ПР7
@app.route('/sort/date')
def sort_by_date(): 
    sorted_tasks = sorted(tasks, key=lambda t: t.get('date', ''), reverse=True)
    return render_template('index.html', tasks=sorted_tasks)

@app.route('/sort/status')
def sort_by_status():
    sorted_tasks = sorted(tasks, key=lambda t: t.get('done', False))
    return render_template('index.html', tasks=sorted_tasks)

@app.route('/sort/priority')
def sort_by_priority():
    priority_order = {'Высокий': 1, 'Обычный': 2, 'Низкий': 3}
    sorted_tasks = sorted(
        tasks,
        key=lambda t: priority_order.get(t.get('priority', 'Обычный'), 2)
    )
    return render_template('index.html', tasks=sorted_tasks)

@app.route('/sort/alpha')
def sort_by_alpha():
    sorted_tasks = sorted(tasks, key=lambda t: t.get('text', '').lower())
    return render_template('index.html', tasks=sorted_tasks)

if __name__ == '__main__':
    app.run(debug=True)
