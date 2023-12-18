from datetime import datetime
from enum import unique
from uuid import UUID, uuid4
from fastapi_users.db import BeanieBaseUser, BeanieUserDatabase
from pydantic import EmailStr, Field
from beanie import Document, Indexed

from typing_extensions import Annotated

class User(BeanieBaseUser, Document):
    pass
