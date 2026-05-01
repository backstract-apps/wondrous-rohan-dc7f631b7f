from sqlalchemy.orm import Session, aliased
from database import SessionLocal
from sqlalchemy import and_, or_
from typing import *
from loguru import logger
from fastapi import Request, UploadFile, HTTPException, status
from fastapi.responses import RedirectResponse, StreamingResponse
import models, schemas
import boto3
import jwt
from datetime import datetime
import requests
import math
import os
import json
import random
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from agents import (
    Agent,
    Runner,
    RunConfig,
    ModelSettings,
    InputGuardrail,
    OutputGuardrail,
)
import agent_session_store as store


load_dotenv()


def convert_to_datetime(date_string):
    if date_string is None:
        return datetime.now()
    if not date_string.strip():
        return datetime.now()
    if "T" in date_string:
        try:
            return datetime.fromisoformat(date_string.replace("Z", "+00:00"))
        except ValueError:
            date_part = date_string.split("T")[0]
            try:
                return datetime.strptime(date_part, "%Y-%m-%d")
            except ValueError:
                return datetime.now()
    else:
        # Try to determine format based on first segment
        parts = date_string.split("-")
        if len(parts[0]) == 4:
            # Likely YYYY-MM-DD format
            try:
                return datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return datetime.now()

        # Try DD-MM-YYYY format
        try:
            return datetime.strptime(date_string, "%d-%m-%Y")
        except ValueError:
            return datetime.now()

        # Fallback: try YYYY-MM-DD if not already tried
        if len(parts[0]) != 4:
            try:
                return datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return datetime.now()

        return datetime.now()


class SessionStoreAdapter:

    def load_session(self, session_id: str) -> dict:
        return store.load_session_memory(session_id)

    def save_session(self, session_id: str, data: dict) -> None:
        store.save_session_memory(session_id, data)


_memory_adapter = SessionStoreAdapter()


async def agent_create_session(body: str):
    """Start a new chat session."""
    meta = store.create_session(title=body, session_id=body)
    return meta


async def agent_get_history(session_id: str):
    """Return the human-readable message history for a session."""
    if not store.get_session(session_id):
        raise HTTPException(404, "Session not found")
    messages = store.get_chat_history(session_id)
    return {"session_id": session_id, "messages": messages}


async def _agent_generate_title(
    first_message: str, run_config: RunConfig, agent: Agent
) -> str:
    """Ask the LLM for a short 4-word session title from the first user message."""
    try:
        result = await asyncio.wait_for(
            Runner.run(
                agent,
                f"Give a 4-word title (no quotes, no punctuation) that summarises this message: {first_message[:300]}",
                run_config=run_config,
            ),
            timeout=15,
        )
        title = str(result.final_output).strip()[:60]
        return title if title else first_message[:40]
    except Exception:
        return first_message[:40]


async def get_app_user_analytics(
    request: Request,
    db: Session,
):

    query = db.query(models.AppUserAnalytics)

    app_user_analytics_all = query.all()
    app_user_analytics_all = (
        [new_data.to_dict() for new_data in app_user_analytics_all]
        if app_user_analytics_all
        else app_user_analytics_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"app_user_analytics_all": app_user_analytics_all},
    }
    return res


async def get_app_user_analytics_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.AppUserAnalytics)
    query = query.filter(and_(models.AppUserAnalytics.id == id))

    app_user_analytics_one = query.first()

    app_user_analytics_one = (
        (
            app_user_analytics_one.to_dict()
            if hasattr(app_user_analytics_one, "to_dict")
            else vars(app_user_analytics_one)
        )
        if app_user_analytics_one
        else app_user_analytics_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"app_user_analytics_one": app_user_analytics_one},
    }
    return res


async def post_app_user_analytics(
    request: Request,
    db: Session,
    raw_data: schemas.PostAppUserAnalytics,
):
    id: Union[int, float] = raw_data.id
    session_id: str = raw_data.session_id
    action: str = raw_data.action
    version: str = raw_data.version
    timestamp: str = raw_data.timestamp
    user_agent: str = raw_data.user_agent
    locale: str = raw_data.locale
    location: str = raw_data.location
    referrer: str = raw_data.referrer
    pathname: str = raw_data.pathname
    href: str = raw_data.href
    created_at: str = convert_to_datetime(raw_data.created_at)

    record_to_be_added = {
        "id": id,
        "href": href,
        "action": action,
        "locale": locale,
        "version": version,
        "location": location,
        "pathname": pathname,
        "referrer": referrer,
        "timestamp": timestamp,
        "created_at": created_at,
        "session_id": session_id,
        "user_agent": user_agent,
    }
    new_app_user_analytics = models.AppUserAnalytics(**record_to_be_added)
    db.add(new_app_user_analytics)
    db.commit()
    db.refresh(new_app_user_analytics)
    app_user_analytics_inserted_record = new_app_user_analytics.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {
            "app_user_analytics_inserted_record": app_user_analytics_inserted_record
        },
    }
    return res


async def put_app_user_analytics_id(
    request: Request,
    db: Session,
    raw_data: schemas.PutAppUserAnalyticsId,
):
    id: Union[int, float] = raw_data.id
    session_id: str = raw_data.session_id
    action: str = raw_data.action
    version: str = raw_data.version
    timestamp: str = raw_data.timestamp
    user_agent: str = raw_data.user_agent
    locale: str = raw_data.locale
    location: str = raw_data.location
    referrer: str = raw_data.referrer
    pathname: str = raw_data.pathname
    href: str = raw_data.href
    created_at: str = convert_to_datetime(raw_data.created_at)

    query = db.query(models.AppUserAnalytics)
    query = query.filter(and_(models.AppUserAnalytics.id == id))
    app_user_analytics_edited_record = query.first()

    if app_user_analytics_edited_record:
        for key, value in {
            "id": id,
            "href": href,
            "action": action,
            "locale": locale,
            "version": version,
            "location": location,
            "pathname": pathname,
            "referrer": referrer,
            "timestamp": timestamp,
            "created_at": created_at,
            "session_id": session_id,
            "user_agent": user_agent,
        }.items():
            setattr(app_user_analytics_edited_record, key, value)

        db.commit()

        db.refresh(app_user_analytics_edited_record)

        app_user_analytics_edited_record = (
            app_user_analytics_edited_record.to_dict()
            if hasattr(app_user_analytics_edited_record, "to_dict")
            else vars(app_user_analytics_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"app_user_analytics_edited_record": app_user_analytics_edited_record},
    }
    return res


async def get_tasks(
    request: Request,
    db: Session,
):

    query = db.query(models.Tasks)

    tasks_all = query.all()
    tasks_all = (
        [new_data.to_dict() for new_data in tasks_all] if tasks_all else tasks_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"tasks_all": tasks_all},
    }
    return res


async def get_tasks_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Tasks)
    query = query.filter(and_(models.Tasks.id == id))

    tasks_one = query.first()

    tasks_one = (
        (tasks_one.to_dict() if hasattr(tasks_one, "to_dict") else vars(tasks_one))
        if tasks_one
        else tasks_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"tasks_one": tasks_one},
    }
    return res


async def post_tasks(
    request: Request,
    db: Session,
    raw_data: schemas.PostTasks,
):
    id: Union[int, float] = raw_data.id
    user_id: Union[int, float] = raw_data.user_id
    title: str = raw_data.title
    description: str = raw_data.description
    status: str = raw_data.status
    priority: str = raw_data.priority
    due_date: str = convert_to_datetime(raw_data.due_date)
    created_at: str = convert_to_datetime(raw_data.created_at)
    updated_at: str = convert_to_datetime(raw_data.updated_at)

    record_to_be_added = {
        "id": id,
        "title": title,
        "status": status,
        "user_id": user_id,
        "due_date": due_date,
        "priority": priority,
        "created_at": created_at,
        "updated_at": updated_at,
        "description": description,
    }
    new_tasks = models.Tasks(**record_to_be_added)
    db.add(new_tasks)
    db.commit()
    db.refresh(new_tasks)
    tasks_inserted_record = new_tasks.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"tasks_inserted_record": tasks_inserted_record},
    }
    return res


async def put_tasks_id(
    request: Request,
    db: Session,
    raw_data: schemas.PutTasksId,
):
    id: Union[int, float] = raw_data.id
    user_id: Union[int, float] = raw_data.user_id
    title: str = raw_data.title
    description: str = raw_data.description
    status: str = raw_data.status
    priority: str = raw_data.priority
    due_date: str = convert_to_datetime(raw_data.due_date)
    created_at: str = convert_to_datetime(raw_data.created_at)
    updated_at: str = convert_to_datetime(raw_data.updated_at)

    query = db.query(models.Tasks)
    query = query.filter(and_(models.Tasks.id == id))
    tasks_edited_record = query.first()

    if tasks_edited_record:
        for key, value in {
            "id": id,
            "title": title,
            "status": status,
            "user_id": user_id,
            "due_date": due_date,
            "priority": priority,
            "created_at": created_at,
            "updated_at": updated_at,
            "description": description,
        }.items():
            setattr(tasks_edited_record, key, value)

        db.commit()

        db.refresh(tasks_edited_record)

        tasks_edited_record = (
            tasks_edited_record.to_dict()
            if hasattr(tasks_edited_record, "to_dict")
            else vars(tasks_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"tasks_edited_record": tasks_edited_record},
    }
    return res


async def delete_tasks_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Tasks)
    query = query.filter(and_(models.Tasks.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        tasks_deleted = record_to_delete.to_dict()
    else:
        tasks_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"tasks_deleted": tasks_deleted},
    }
    return res


async def get_users(
    request: Request,
    db: Session,
):

    query = db.query(models.Users)

    users_all = query.all()
    users_all = (
        [new_data.to_dict() for new_data in users_all] if users_all else users_all
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"users_all": users_all},
    }
    return res


async def get_users_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.id == id))

    users_one = query.first()

    users_one = (
        (users_one.to_dict() if hasattr(users_one, "to_dict") else vars(users_one))
        if users_one
        else users_one
    )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"users_one": users_one},
    }
    return res


async def post_users(
    request: Request,
    db: Session,
    raw_data: schemas.PostUsers,
):
    id: Union[int, float] = raw_data.id
    email: str = raw_data.email
    password: str = raw_data.password
    created_at: str = convert_to_datetime(raw_data.created_at)

    record_to_be_added = {
        "id": id,
        "email": email,
        "password": password,
        "created_at": created_at,
    }
    new_users = models.Users(**record_to_be_added)
    db.add(new_users)
    db.commit()
    db.refresh(new_users)
    users_inserted_record = new_users.to_dict()

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"users_inserted_record": users_inserted_record},
    }
    return res


async def put_users_id(
    request: Request,
    db: Session,
    raw_data: schemas.PutUsersId,
):
    id: Union[int, float] = raw_data.id
    email: str = raw_data.email
    password: str = raw_data.password
    created_at: str = convert_to_datetime(raw_data.created_at)

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.id == id))
    users_edited_record = query.first()

    if users_edited_record:
        for key, value in {
            "id": id,
            "email": email,
            "password": password,
            "created_at": created_at,
        }.items():
            setattr(users_edited_record, key, value)

        db.commit()

        db.refresh(users_edited_record)

        users_edited_record = (
            users_edited_record.to_dict()
            if hasattr(users_edited_record, "to_dict")
            else vars(users_edited_record)
        )

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"users_edited_record": users_edited_record},
    }
    return res


async def delete_users_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        users_deleted = record_to_delete.to_dict()
    else:
        users_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"users_deleted": users_deleted},
    }
    return res


async def delete_app_user_analytics_id(
    request: Request,
    db: Session,
    id: Union[int, float],
):

    query = db.query(models.AppUserAnalytics)
    query = query.filter(and_(models.AppUserAnalytics.id == id))

    record_to_delete = query.first()
    if record_to_delete:
        db.delete(record_to_delete)
        db.commit()
        app_user_analytics_deleted = record_to_delete.to_dict()
    else:
        app_user_analytics_deleted = record_to_delete

    res = {
        "status": 200,
        "message": "This is the default message.",
        "data": {"app_user_analytics_deleted": app_user_analytics_deleted},
    }
    return res


async def get_platform_auth_package_mayson_sso_auth_callback(
    request: Request,
    db: Session,
):

    user_identity: str = "i"

    user_password: str = "top_secret_area_51"

    from passlib.hash import md5_crypt

    encrypt_pass = md5_crypt.hash(user_password)

    # get user email from request

    try:
        param_obj = dict(request.query_params)

        not_found_page = "https://mayson.dev/not-found"
        user_identity = param_obj.get(
            "user_email", "no-user-identity-received-from-backend"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == user_identity))
    has_a_record = query.count() > 0

    if has_a_record:
        pass

    else:

        record_to_be_added = {"email": user_identity, "password": encrypt_pass}
        new_users = models.Users(**record_to_be_added)
        db.add(new_users)
        db.commit()
        db.refresh(new_users)
        post_user_record = new_users.to_dict()

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == user_identity))

    user_record = query.first()

    user_record = (
        (
            user_record.to_dict()
            if hasattr(user_record, "to_dict")
            else vars(user_record)
        )
        if user_record
        else user_record
    )

    import jwt
    from datetime import timezone

    secret_key = """TMF5KImMBQDC-v2CfMpv2a6woKWa3RMrucKfnPBtsgY="""
    bs_jwt_payload = {
        "exp": int(datetime.now(timezone.utc).timestamp() + 86400),
        "data": user_record,
    }

    generated_jwt = jwt.encode(bs_jwt_payload, secret_key, algorithm="HS256")

    # define client

    try:
        request_token = generated_jwt or "no-generated-jwt"
        request_provider = param_obj.get("provider", "no-provider-from-backend")
        final_url = f'{param_obj.get("frontend-redirect", not_found_page)}?token={request_token}&provider={request_provider}'

        return RedirectResponse(url=final_url)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"message": "success_response"},
    }
    return res


async def get_platform_auth_package_mayson_sso_auth_login_google(
    request: Request,
    db: Session,
):

    # define client

    try:
        import httpx

        async def google_login():
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": "Bearer v4.public.eyJlbWFpbF9pZCI6ICJzaGl2YW00Mzg2ODdAeW9wbWFpbC5jb20iLCAidXNlcl9pZCI6ICI0YmE4ZDMyZDdhMDM0OGE5ODdhYmNmZTIzZDU3YmYyYyIsICJvcmdfaWQiOiAiTkEiLCAic3RhdGUiOiAic2lnbnVwIiwgInJvbGVfbmFtZSI6ICJOQSIsICJyb2xlX2lkIjogIk5BIiwgInBsYW5faWQiOiAiMTEzIiwgImFjY291bnRfdmVyaWZpZWQiOiAiMSIsICJhY2NvdW50X3N0YXR1cyI6ICIwIiwgInVzZXJfbmFtZSI6ICI0YmE4ZDMyZDdhMDM0OGE5ODdhYmNmZTIzZDU3YmYyYyIsICJzaWdudXBfcXVlc3Rpb24iOiAwLCAidG9rZW5fbGltaXQiOiBudWxsLCAidG9rZW5fdHlwZSI6ICJhY2Nlc3MiLCAiZXhwIjogMTc3ODIzMzU5MSwgImV4cGlyeV90aW1lIjogMTc3ODIzMzU5MX0mEcph-GgCNjBhpp4Qb06BTibgHn13GiNnbBzsf5cGDkiRs_UDK4O_BHfG0CcFEM_844Nn80eG4NsWJFpQhqUK",
                    "Content-Type": "application/json",
                }

                res = await client.get(
                    "https://api-release.beemerbenzbentley.site/sigma/api/v1/sso/auth/google/login?collection_id=coll_40b587e0e76f464c8cb78a581d06c1c5",
                    headers=headers,
                )

            res.raise_for_status()

            try:
                response_obj = dict(res.json())
                final_url = response_obj.get("value")
                return final_url
            except Exception as e:
                return f"https://mayson.dev/not-found?reason={str(e)}"

        return RedirectResponse(url=await google_login())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"message": "success_response"},
    }
    return res


async def post_platform_auth_package_mayson_auth_user_login(
    request: Request,
    db: Session,
    raw_data: schemas.PostPlatformAuthPackageMaysonAuthUserLogin,
):
    email: str = raw_data.email
    password: str = raw_data.password

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == email))

    oneRecord = query.first()

    oneRecord = (
        (oneRecord.to_dict() if hasattr(oneRecord, "to_dict") else vars(oneRecord))
        if oneRecord
        else oneRecord
    )

    if oneRecord:
        from passlib.hash import md5_crypt

        password_hash_mayson = oneRecord["password"]
        password_valid = md5_crypt.verify(password, password_hash_mayson)
        if password_valid:
            validated_password = True
        else:
            validated_password = False
    else:
        validated_password = False

    login_status: str = "Login initiated"

    if validated_password:

        login_status = "Login success"

    else:

        raise HTTPException(status_code=401, detail="Bad credentials.")

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == email))

    user_record = query.first()

    user_record = (
        (
            user_record.to_dict()
            if hasattr(user_record, "to_dict")
            else vars(user_record)
        )
        if user_record
        else user_record
    )

    import jwt
    from datetime import timezone

    secret_key = """TMF5KImMBQDC-v2CfMpv2a6woKWa3RMrucKfnPBtsgY="""
    bs_jwt_payload = {
        "exp": int(datetime.now(timezone.utc).timestamp() + 86400),
        "data": user_record,
    }

    generated_jwt = jwt.encode(bs_jwt_payload, secret_key, algorithm="HS256")

    login_status = "Login successful"

    res = {
        "status": 200,
        "message": "Login successful",
        "data": {"jwt": generated_jwt, "login_status": login_status},
    }
    return res


async def get_platform_auth_package_mayson_sso_auth_me(
    request: Request,
    db: Session,
):

    # get auth header

    try:
        auth_header = request.headers.get("authorization")
        auth_header = (
            auth_header[7:]
            if auth_header and auth_header.lower().startswith("bearer ")
            else auth_header
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    import jwt

    try:
        user_profile = jwt.decode(
            auth_header,
            """TMF5KImMBQDC-v2CfMpv2a6woKWa3RMrucKfnPBtsgY=""",
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token.")

    # profile_data = user_profile["data"]

    try:
        profile_data = user_profile["data"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

    res = {
        "status": 200,
        "message": "The request has been successfully processed",
        "data": {"user_profile": profile_data},
    }
    return res


async def post_platform_auth_package_mayson_auth_user_register(
    request: Request,
    db: Session,
    raw_data: schemas.PostPlatformAuthPackageMaysonAuthUserRegister,
):
    email: str = raw_data.email
    password: str = raw_data.password

    query = db.query(models.Users)
    query = query.filter(and_(models.Users.email == email))

    existing_record = query.first()

    existing_record = (
        (
            existing_record.to_dict()
            if hasattr(existing_record, "to_dict")
            else vars(existing_record)
        )
        if existing_record
        else existing_record
    )

    if existing_record:

        raise HTTPException(status_code=400, detail="User already exists.")
    else:
        pass

    from passlib.hash import md5_crypt

    encrypt_pass = md5_crypt.hash(password)

    record_to_be_added = {"email": email, "password": encrypt_pass}
    new_users = models.Users(**record_to_be_added)
    db.add(new_users)
    db.commit()
    db.refresh(new_users)
    post_user_record = new_users.to_dict()

    res = {"status": 200, "message": "User registered successfully", "data": {}}
    return res
