from pydantic import BaseModel,Field,field_validator

import datetime

import uuid

from typing import Any, Dict, List,Optional,Tuple,Union

import re

class AppUserAnalytics(BaseModel):
    id: int
    session_id: str
    action: str
    version: Optional[str]=None
    timestamp: Any
    user_agent: Optional[str]=None
    locale: Optional[str]=None
    location: Optional[str]=None
    referrer: Optional[str]=None
    pathname: Optional[str]=None
    href: Optional[str]=None
    created_at: Any


class ReadAppUserAnalytics(BaseModel):
    id: int
    session_id: str
    action: str
    version: Optional[str]=None
    timestamp: Any
    user_agent: Optional[str]=None
    locale: Optional[str]=None
    location: Optional[str]=None
    referrer: Optional[str]=None
    pathname: Optional[str]=None
    href: Optional[str]=None
    created_at: Any
    class Config:
        from_attributes = True


class Tasks(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]=None
    status: str
    priority: str
    due_date: Optional[str]=None
    created_at: Optional[str]=None
    updated_at: Optional[str]=None


class ReadTasks(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]=None
    status: str
    priority: str
    due_date: Optional[str]=None
    created_at: Optional[str]=None
    updated_at: Optional[str]=None
    class Config:
        from_attributes = True


class Users(BaseModel):
    id: int
    email: str
    password: str
    created_at: Optional[str]=None


class ReadUsers(BaseModel):
    id: int
    email: str
    password: str
    created_at: Optional[str]=None
    class Config:
        from_attributes = True




class PostAppUserAnalytics(BaseModel):
    id: Union[int, float] = Field(...)
    session_id: str = Field(..., max_length=100)
    action: str = Field(..., max_length=100)
    version: Optional[str]=None
    timestamp: str = Field(..., max_length=100)
    user_agent: Optional[str]=None
    locale: Optional[str]=None
    location: Optional[str]=None
    referrer: Optional[str]=None
    pathname: Optional[str]=None
    href: Optional[str]=None
    created_at: str = Field(..., max_length=100)

    class Config:
        from_attributes = True



class PutAppUserAnalyticsId(BaseModel):
    id: Union[int, float] = Field(...)
    session_id: str = Field(..., max_length=100)
    action: str = Field(..., max_length=100)
    version: Optional[str]=None
    timestamp: str = Field(..., max_length=100)
    user_agent: Optional[str]=None
    locale: Optional[str]=None
    location: Optional[str]=None
    referrer: Optional[str]=None
    pathname: Optional[str]=None
    href: Optional[str]=None
    created_at: str = Field(..., max_length=100)

    class Config:
        from_attributes = True



class PostTasks(BaseModel):
    id: Union[int, float] = Field(...)
    user_id: Union[int, float] = Field(...)
    title: str = Field(..., max_length=255)
    description: Optional[str]=None
    status: str = Field(..., max_length=20)
    priority: str = Field(..., max_length=10)
    due_date: Optional[str]=None
    created_at: Optional[str]=None
    updated_at: Optional[str]=None

    class Config:
        from_attributes = True



class PutTasksId(BaseModel):
    id: Union[int, float] = Field(...)
    user_id: Union[int, float] = Field(...)
    title: str = Field(..., max_length=255)
    description: Optional[str]=None
    status: str = Field(..., max_length=20)
    priority: str = Field(..., max_length=10)
    due_date: Optional[str]=None
    created_at: Optional[str]=None
    updated_at: Optional[str]=None

    class Config:
        from_attributes = True



class PostUsers(BaseModel):
    id: Union[int, float] = Field(...)
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    created_at: Optional[str]=None

    class Config:
        from_attributes = True



class PutUsersId(BaseModel):
    id: Union[int, float] = Field(...)
    email: str = Field(..., max_length=255)
    password: str = Field(..., max_length=255)
    created_at: Optional[str]=None

    class Config:
        from_attributes = True



class PostPlatformAuthPackageMaysonAuthUserLogin(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)

    class Config:
        from_attributes = True



class PostPlatformAuthPackageMaysonAuthUserRegister(BaseModel):
    email: str = Field(..., max_length=100)
    password: str = Field(..., max_length=100)

    class Config:
        from_attributes = True



# Query Parameter Validation Schemas

class GetAppUserAnalyticsIdQueryParams(BaseModel):
    """Query parameter validation for get_app_user_analytics_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class GetTasksIdQueryParams(BaseModel):
    """Query parameter validation for get_tasks_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class DeleteTasksIdQueryParams(BaseModel):
    """Query parameter validation for delete_tasks_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class GetUsersIdQueryParams(BaseModel):
    """Query parameter validation for get_users_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class DeleteUsersIdQueryParams(BaseModel):
    """Query parameter validation for delete_users_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True


class DeleteAppUserAnalyticsIdQueryParams(BaseModel):
    """Query parameter validation for delete_app_user_analytics_id"""
    id: int = Field(..., ge=1, description="Id")

    class Config:
        populate_by_name = True
