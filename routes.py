from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile,Query, Form
from sqlalchemy.orm import Session
from typing import List,Annotated
import service, models, schemas
from fastapi import Query
from database import SessionLocal
from middleware.application_middleware import platform_auth_platform_auth_middleware_group_dependency, default_dependency


router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/app_user_analytics/')
async def get_app_user_analytics(request: Request, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.get_app_user_analytics(request, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/app_user_analytics/id/')
async def get_app_user_analytics_id(request: Request, query: schemas.GetAppUserAnalyticsIdQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.get_app_user_analytics_id(request, db, query.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/app_user_analytics/')
async def post_app_user_analytics(request: Request, raw_data: schemas.PostAppUserAnalytics, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.post_app_user_analytics(request, db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put('/app_user_analytics/id/')
async def put_app_user_analytics_id(request: Request, raw_data: schemas.PutAppUserAnalyticsId, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.put_app_user_analytics_id(request, db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/tasks/')
async def get_tasks(request: Request, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.get_tasks(request, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/tasks/id/')
async def get_tasks_id(request: Request, query: schemas.GetTasksIdQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.get_tasks_id(request, db, query.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/tasks/')
async def post_tasks(request: Request, raw_data: schemas.PostTasks, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.post_tasks(request, db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put('/tasks/id/')
async def put_tasks_id(request: Request, raw_data: schemas.PutTasksId, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.put_tasks_id(request, db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete('/tasks/id/')
async def delete_tasks_id(request: Request, query: schemas.DeleteTasksIdQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.delete_tasks_id(request, db, query.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/users/')
async def get_users(request: Request, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.get_users(request, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/users/id/')
async def get_users_id(request: Request, query: schemas.GetUsersIdQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.get_users_id(request, db, query.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/users/')
async def post_users(request: Request, raw_data: schemas.PostUsers, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.post_users(request, db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put('/users/id/')
async def put_users_id(request: Request, raw_data: schemas.PutUsersId, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.put_users_id(request, db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete('/users/id/')
async def delete_users_id(request: Request, query: schemas.DeleteUsersIdQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.delete_users_id(request, db, query.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.delete('/app_user_analytics/id/')
async def delete_app_user_analytics_id(request: Request, query: schemas.DeleteAppUserAnalyticsIdQueryParams = Depends(), db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.delete_app_user_analytics_id(request, db, query.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/platform_auth_package/mayson/sso/auth/callback/')
async def get_platform_auth_package_mayson_sso_auth_callback(request: Request, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.get_platform_auth_package_mayson_sso_auth_callback(request, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/platform_auth_package/mayson/sso/auth/login/google')
async def get_platform_auth_package_mayson_sso_auth_login_google(request: Request, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.get_platform_auth_package_mayson_sso_auth_login_google(request, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/platform_auth_package/mayson/auth/user/login')
async def post_platform_auth_package_mayson_auth_user_login(request: Request, raw_data: schemas.PostPlatformAuthPackageMaysonAuthUserLogin, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.post_platform_auth_package_mayson_auth_user_login(request, db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get('/platform_auth_package/mayson/sso/auth/me')
async def get_platform_auth_package_mayson_sso_auth_me(request: Request, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.get_platform_auth_package_mayson_sso_auth_me(request, db)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post('/platform_auth_package/mayson/auth/user/register')
async def post_platform_auth_package_mayson_auth_user_register(request: Request, raw_data: schemas.PostPlatformAuthPackageMaysonAuthUserRegister, db: Session = Depends(get_db), protected_deps_1: dict = Depends(platform_auth_platform_auth_middleware_group_dependency), protected_deps_2: dict = Depends(default_dependency),  ):
    try:
        return await service.post_platform_auth_package_mayson_auth_user_register(request, db, raw_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

