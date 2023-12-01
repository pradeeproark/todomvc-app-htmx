from collections import namedtuple
from dataclasses import dataclass
from http import HTTPStatus
import typing
from uuid import uuid4
from flask import Flask, render_template, request, Response, send_from_directory
from flask import session

app = Flask(__name__, static_folder='static',static_url_path='')
app.secret_key = '20f0507d6e99e96c96be1f50cfb3a0c44b159141ca97edf9400dad41a270ed66'

@dataclass
class Todo:
    id: str
    label: str
    status: bool
    editMode: bool

@dataclass
class State:
    currentStatusFilter: str
    hideSection: bool
    tobeCompletedCount: int
    clearCompleted: bool
    selectedIndex: typing.Union[int, None]

def fixTodo(todo: Todo) -> Todo:
    if isinstance(todo, dict):
        return Todo(**todo)
    return todo

def updateState(state: State, todos: list[Todo]):
    if isinstance(state,dict):
        state = State(**state)
    todos = list(map(fixTodo, todos))
    newState = State(state.currentStatusFilter, hideSection=len(todos) == 0, tobeCompletedCount=sum(todo.status == False for todo in todos), clearCompleted = sum(todo.status == True for todo in todos) > 0, selectedIndex = state.selectedIndex)
    session["currentState"] = newState
    session["todos"] = todos
    return newState


@app.route('/node_modules/<path:filename>')
def nodeModules(filename):
    return send_from_directory(app.root_path + '/node_modules/', filename, conditional=True)

def getInitialTodos():
    return []

def getInitialState():
    return State("All", True, 0, True, None)

StateTodos = namedtuple('StateTodos', ['state', 'todos'])

def getState() -> typing.Tuple[State, list[Todo]]:
    if not "currentState" in session:
        session["currentState"] = updateState(getInitialState(), getInitialTodos())
    if not "todos" in session:
        session["todos"] = getInitialTodos()
    state = session["currentState"]
    todos = session["todos"]
    if isinstance(session["currentState"],dict):
        state = State(**state)
    todos = list(map(fixTodo, todos))
    return StateTodos(state=state, todos=todos)

@app.route("/")
def index():   
    return render_template('index.html', ctx=getState())

@app.route("/addTodo", methods=['POST'])
def addTodo():
    currentState, todos = getState()
    newTodoLabel = request.form.get('new-todo').strip()
    newTodo = None
    if len(newTodoLabel) > 0:
        newTodo = Todo(str(uuid4()),newTodoLabel, False, False)
        todos.append(newTodo)
        currentState = updateState(currentState, todos)
    return render_template('edit-todo.html', ctx=getState(), todo=newTodo)

@app.route("/editTodo/<id>", methods=['GET'])
def editTodo(id):
    currentState, todos = getState()
    for index,item in enumerate(todos):
        if item.id == id:
            selectedTodo = todos[index]
            selectedTodo.editMode = not selectedTodo.editMode 
            currentState.selectedIndex = index
    currentState = updateState(currentState, todos)
    return render_template("edit-todo.html", ctx=getState())

@app.route("/updateTodo/<id>", methods=['POST'])
def updateTodo(id):
    currentState, todos = getState()
    updatedLabel = request.form.get('edit-todo').strip()
    currentState.selectedIndex = None
    for index,item in enumerate(todos):
        if item.id == id:
            if len(updatedLabel) == 0:
                return deleteTodo(id)
            item.label = updatedLabel
            item.editMode = False
            currentState.selectedIndex = index
    currentState = updateState(currentState, todos)
    return render_template("edit-todo.html", ctx=getState())


@app.route("/deleteTodo/<id>",methods=['DELETE'])
def deleteTodo(id):
    currentState, todos = getState()
    selectedTodo = next((todo for todo in todos if todo.id == id), None)
    if selectedTodo:
        todos.remove(selectedTodo)
        currentState = updateState(currentState, todos)
        return render_template("footer-update.html", ctx=getState())
    else:
        return Response(status=HTTPStatus.NOT_FOUND)

@app.route("/markCompleted",methods=['POST'])
def markCompleted():
    currentState, todos = getState()
    for todo in todos:
        todo.status = True
    updateState(currentState, todos)
    return getTodos("All")

@app.route("/toggleStatus/<id>",methods=['POST'])
def toggleStatus(id):
    currentState, todos = getState()
    currentState.selectedIndex = None
    for index,item in enumerate(todos):
        if item.id == id:
            selectedTodo = todos[index]
            selectedTodo.status = not selectedTodo.status
            currentState.selectedIndex = index
    currentState = updateState(currentState, todos)
    return render_template("edit-todo.html", ctx=getState())

@app.route("/clearCompleted", methods=['POST'])
def clearCompleted():
    currentState, todos = getState()
    clearedTodos = [todo for todo in todos if not todo.status]
    updateState(currentState, clearedTodos)
    return getTodos("All")

@app.route("/todos", defaults={"status":"All"})
@app.route("/todos/<status>")
def getTodos(status):
    currentState, todos = getState()
    currentState.currentStatusFilter = status
    filteredItems = todos
    if currentState.currentStatusFilter == "completed":
        filteredItems = [item for item in filteredItems if item.status == True]
    elif currentState.currentStatusFilter == "active":
        filteredItems = [item for item in filteredItems if item.status == False]
    currentState = updateState(currentState, todos)
    return render_template('todo-list.html', ctx=getState())

if __name__ == '__main__':
    app.run()
