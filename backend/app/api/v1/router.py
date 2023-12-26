from fastapi import APIRouter
from backend.app.api.v1.handlers import user, todo, vvz
from backend.app.api.v1.handlers.user import auth_backend, current_active_user, fastapi_users
from backend.app.schemas.user import UserRead, UserCreate, UserUpdate


router = APIRouter()

router.include_router(todo.todo_router, prefix="/todo", tags=["todo"])
router.include_router(vvz.vvz_router, prefix="/vvz", tags=["vvz"])


router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)