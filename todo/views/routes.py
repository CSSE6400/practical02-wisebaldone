from flask import Blueprint, jsonify, request
from todo.models import db
from todo.models.todo import Todo
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.route('/health')
def health():
    """Return a status of 'ok' if the server is running and listening to request"""
    return jsonify({"status": "ok"})


@api.route('/todos', methods=['GET'])
def get_todos():
    """Return the list of todo items"""
    todos = Todo.query.all()
    result = []
    for todo in todos:
        result.append(todo.to_dict())
    return jsonify(result)

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
    return jsonify({'message': 'Todo deleted'}), 200
 
