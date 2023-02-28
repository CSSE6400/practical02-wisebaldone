from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime, timedelta

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/health')
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    """Return the list of todo items"""
    completed = request.args.get('completed')
    window = request.args.get('window')

    # validate completed and window
    if completed:
        if completed not in ['true', 'false']:
            return jsonify({'error': 'invalid completed value'}), 400
        completed = completed == 'true'
    if window:
        try:
            window = int(window)
        except ValueError:
            return jsonify({'error': 'invalid window value'}), 400
        if window < 0:
            return jsonify({'error': 'invalid window value'}), 400

    items = Todo.query
    if completed:
        items = items.filter_by(completed=completed)
    if window:
        future = datetime.utcnow() + timedelta(days=window)
        items = items.filter(Todo.deadline_at <= future)
    return jsonify([item.to_dict() for item in items.all()])

@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Return the details of a todo item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())


@api.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo item and return the created item"""
        # Check that we got a json request
    if not request.is_json:
        return jsonify({'error': 'invalid content type'}), 400

    # Check that we got a title as its mandatory
    if not request.json.get('title'):
        return jsonify({'error': 'title is required'}), 400

    # validate request by making sure it can only have the fields title, description, completed, deadline_at
    for key in request.json.keys():
        if key not in ['title', 'description', 'completed', 'deadline_at']:
            return jsonify({'error': 'invalid request'}), 400

    # Title cant be an empty string
    if request.json.get('title') == '':
        return jsonify({'error': 'title cant be empty'}), 400

    todo = Todo(
        title=request.json.get('title'),
        description=request.json.get('description'),
        completed=request.json.get('completed', False),
    )
    if 'deadline_at' in request.json:
        todo.deadline_at = datetime.fromisoformat(request.json.get('deadline_at'))

    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201

@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update a todo item and return the updated item"""
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404

    if not request.is_json:
        return jsonify({'error': 'invalid content type'}), 400

    # validate request by making sure it can only have the fields title, description, completed, deadline_at
    if not all(key in ['title', 'description', 'completed', 'deadline_at'] for key in request.json.keys()):
        return jsonify({'error': 'invalid request'}), 400

    if 'title' in request.json and request.json['title'] == '':
        return jsonify({'error': 'title cant be empty'}), 400

    todo.title = request.json.get('title', todo.title)
    todo.description = request.json.get('description', todo.description)
    todo.completed = request.json.get('completed', todo.completed)
    todo.deadline_at = request.json.get('deadline_at', todo.deadline_at)
    db.session.commit()

    return jsonify(todo.to_dict())

@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo item and return the deleted item"""
    todo = Todo.query.get(todo_id)

    if todo is None:
        return jsonify(), 200

    db.session.delete(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 200
