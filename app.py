from dataclasses import dataclass
from http import HTTPStatus
from uuid import uuid4
from flask import Flask, render_template, request, Response, send_from_directory


app = Flask(__name__, static_folder='static',static_url_path='')


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

currentState = State("All", True, 0, True)
todoItems: list[Todo] = [Todo(id=str(uuid4()), label="Taste JavaScript",status=True, editMode=False), Todo(id=str(uuid4()), label="Buy a unicorn",status=False, editMode=False)]

def updateState(state: State, todos):
    return State(state.currentStatusFilter, hideSection=len(todos) == 0, tobeCompletedCount=sum(todo.status == False for todo in todos), clearCompleted = sum(todo.status == True for todo in todos) > 0)




@app.route('/node_modules/<path:filename>')
def nodeModules(filename):
    return send_from_directory(app.root_path + '/node_modules/', filename, conditional=True)

@app.route("/")
def index():
    global currentState
    currentState = updateState(currentState, todoItems)
    return render_template('index.html', todos=todoItems, currentState=currentState)

@app.route("/addTodo", methods=['POST'])
def addTodo():
    global currentState
    newTodoLabel = request.form.get('new-todo').strip()
    if len(newTodoLabel) > 0:
        todoItems.append(Todo(str(uuid4()),newTodoLabel, False, False))
        currentState = updateState(currentState, todoItems)
    return render_template('todo-list.html',todos=todoItems, currentState=currentState)

@app.route("/editTodo/<id>", methods=['GET'])
def editTodo(id):
    global currentState
    selectedTodo = next(todo for todo in todoItems if todo.id == id)
    selectedTodo.editMode = not selectedTodo.editMode 
    currentState = updateState(currentState, todoItems)
    return render_template("edit-todo.html", todo=selectedTodo, currentState=currentState)

@app.route("/updateTodo/<id>", methods=['POST'])
def updateTodo(id):
    global currentState
    updatedLabel = request.form.get('edit-todo').strip()
    selectedIndex = None
    for index,item in enumerate(todoItems):
        if item.id == id:
            if len(updatedLabel) == 0:
                return deleteTodo(id)
            item.label = updatedLabel
            item.editMode = False
            selectedIndex = index
    currentState = updateState(currentState, todoItems)
    return render_template("edit-todo.html", todo=todoItems[selectedIndex], currentState=currentState)


@app.route("/deleteTodo/<id>",methods=['DELETE'])
def deleteTodo(id):
    global currentState
    selectedTodo = next((todo for todo in todoItems if todo.id == id), None)
    if selectedTodo:
        todoItems.remove(selectedTodo)
        currentState = updateState(currentState, todoItems)
        return render_template("footer-update.html", currentState=currentState)
    else:
        return Response(status=HTTPStatus.NOT_FOUND)

@app.route("/toggleStatus/<id>",methods=['POST'])
def toggleStatus(id):
    global currentState
    selectedTodo = next((todo for todo in todoItems if todo.id == id), None)
    if selectedTodo:
        selectedTodo.status = not selectedTodo.status
        currentState = updateState(currentState, todoItems)
        return render_template("edit-todo.html", todo=selectedTodo, currentState=currentState)
    else:
        return Response(status=HTTPStatus.NOT_FOUND)

@app.route("/todos", defaults={"status":"All"})
@app.route("/todos/<status>")
def getTodos(status):
    global currentState
    currentState.currentStatusFilter = status
    filteredItems = todoItems
    if currentState.currentStatusFilter == "completed":
        filteredItems = [item for item in filteredItems if item.status == True]
    elif currentState.currentStatusFilter == "active":
        filteredItems = [item for item in filteredItems if item.status == False]
    currentState = updateState(currentState, todoItems)
    return render_template('todo-list.html',todos=filteredItems, currentState=currentState)

if __name__ == '__main__':
    app.run()
