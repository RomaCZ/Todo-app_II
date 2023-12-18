from uuid import UUID
from fastapi import APIRouter, Depends
from backend.app.schemas.todo import TodoOut, TodoCreate, TodoUpdate
from backend.app.models.user import User
from backend.app.services.todo import TodoService
from backend.app.api.v1.handlers.user import current_active_user
from backend.app.models.todo import Todo


todo_router = APIRouter()


@todo_router.get("/", summary="Get all the todos of the user", response_model=TodoOut)
async def list(current_user: User = Depends(current_active_user)):
    return await TodoService.list_todos(current_user)

@todo_router.post('/create', summary="Create Todo", response_model=Todo)
async def create_todo(data: TodoCreate, current_user: User = Depends(current_active_user)):
    return await TodoService.create_todo(current_user, data)


@todo_router.get('/{todo_id}', summary="Get a todo by todo_id", response_model=TodoOut)
async def retrieve(todo_id: UUID, current_user: User = Depends(current_active_user)):
    return await TodoService.retrieve_todo(current_user, todo_id)


@todo_router.put('/{todo_id}', summary="Update todo by todo_id", response_model=TodoOut)
async def update(todo_id: UUID, data: TodoUpdate, current_user: User = Depends(current_active_user)):
    return await TodoService.update_todo(current_user, todo_id, data)


@todo_router.delete('/{todo_id}', summary="Delete todo by todo_id")
async def delete(todo_id: UUID, current_user: User = Depends(current_active_user)):
    await TodoService.delete_todo(current_user, todo_id)
    return None