"""
Auto-generated middleware file
Contains middleware functions and groups defined in the collection
"""

import os
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, List, Dict, Any
import jwt
from clerk_backend_api import Clerk
from clerk_backend_api.security.types import AuthenticateRequestOptions
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from textwrap import dedent


# Middleware: Auth Package Middleware
# Slug: auth_package_middleware
async def auth_package_middleware(request: Request) -> Dict[str, Any]:
    """
    Auth Package Middleware
    Generated from middleware ID: mid_3c3d2e85511641d484b69df6d4833dac
    """
    try:
        # Authorization:Bearer  = request.headers.get('Authorization')

        import logging
        import os
        import jwt
        from fastapi import HTTPException
        from sqlalchemy import text
        from database import SessionLocal

        # Configure logging
        logger = logging.getLogger(__name__)

        # Define public paths that don't require authentication
        public_paths = [
            "/mayson/auth/2fa/email/login",
            "/mayson/auth/2fa/email/register",
            "/mayson/auth/2fa/email/verify",
            "/mayson/auth/otp/email/login",
            "/mayson/auth/otp/email/verify",
            "/mayson/auth/user/login",
            "/mayson/auth/user/register",
            "/mayson/sso/auth/callback/",
            "/mayson/sso/auth/login/github",
            "/mayson/sso/auth/login/google",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/metrics",
            "/health",
            "/healthz",
            "/favicon.ico",
        ]

        # Get the request path
        request_path = request.url.path

        # Check if any public path is in the request path
        if any(public_path in request_path for public_path in public_paths):
            logger.debug(f"Skipping authentication for public path: {request_path}")
            return {}

        # Get configuration from environment variables
        auth_package_secret_key = """TMF5KImMBQDC-v2CfMpv2a6woKWa3RMrucKfnPBtsgY="""
        auth_package_encryption = os.getenv("AUTH_P_ENCRYPTION", "HS256")
        auth_package_existing_db = (
            os.getenv("AUTH_P_EXISTING_DB", "true").lower() == "true"
        )
        auth_package_table_name = os.getenv("AUTH_P_TABLE_NAME", "mayson_platform_auth")
        auth_package_identity_key = os.getenv("AUTH_P_IDENTITY_KEY", "email")

        # Extract JWT token from Authorization header
        auth_header = request.headers.get("Authorization") or request.headers.get(
            "authorization"
        )

        if not auth_header:
            logger.warning(f"No Authorization header found for {request.url.path}")
            raise HTTPException(status_code=401, detail="Authorization header missing")

        # Extract token from "Bearer <token>" format
        token = None
        if auth_header.startswith("Bearer ") or auth_header.startswith("bearer "):
            token = auth_header[7:]
        else:
            token = auth_header

        try:
            # Decode and verify JWT token
            decoded_token = jwt.decode(
                token, auth_package_secret_key, algorithms=[auth_package_encryption]
            )

            logger.debug(
                f"JWT decoded successfully. Token contains: {list(decoded_token.keys())}"
            )

            # Extract user data from the 'data' field (as per your login service structure)
            if "data" not in decoded_token:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token structure: 'data' field not found",
                )

            user_data = decoded_token["data"]

            # Validate against database if enabled
            if auth_package_existing_db:
                if auth_package_identity_key not in user_data:
                    raise HTTPException(
                        status_code=401,
                        detail=f"Invalid token: required field '{auth_package_identity_key}' not found in token data",
                    )

                token_value = user_data[auth_package_identity_key]

                # Validate user exists in database
                db = SessionLocal()
                try:
                    query = text(
                        f"SELECT COUNT(*) FROM {auth_package_table_name} WHERE {auth_package_identity_key} = :value"
                    )
                    result = db.execute(query, {"value": token_value})
                    count = result.scalar()

                    if count == 0:
                        logger.warning(f"User {token_value} not found in database")
                        raise HTTPException(
                            status_code=401,
                            detail="Invalid token: user not found or inactive",
                        )

                    logger.debug(f"User {token_value} validated successfully")
                except Exception as e:
                    logger.error(f"Database validation error: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Error validating token against database: {str(e)}",
                    )
                finally:
                    db.close()

            # Store decoded token in request state for use in route handlers
            request.state.auth_package_middleware = {
                "table_data": {
                    "table_name": auth_package_table_name,
                    "identity_key": auth_package_identity_key,
                }
            }
            request.state.decoded_token = decoded_token
            request.state.token_user_data = user_data
            request.state.token_user = user_data.get(auth_package_identity_key)

            logger.debug(
                f"Token validated successfully for user: {user_data.get(auth_package_identity_key)}"
            )

            return {"user_data": user_data, "decoded_token": decoded_token}

        except jwt.ExpiredSignatureError:
            logger.warning(f"JWT token has expired for {request.url.path}")
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token for {request.url.path}: {str(e)}")
            raise HTTPException(status_code=401, detail="Invalid token")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error during authentication: {str(e)}",
            )

        return {}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Middleware error: {str(e)}")


# Middleware: CORS Middleware
# Slug: cors_middleware
async def cors_middleware(request: Request) -> Dict[str, Any]:
    """
    CORS Middleware
    Generated from middleware ID: mid_ee29dd4d6bef4290b809626a32f75284
    """
    try:

        def setup_cors_middleware(app: FastAPI):
            """
            Setup CORS middleware with configuration from environment variables
            """

            # Get CORS configuration from environment variables
            origins = os.getenv("CORS_ORIGIN", "*").split(",")
            methods = os.getenv("CORS_METHOD", "GET,POST,PUT,DELETE,OPTIONS").split(",")
            allowed_headers = os.getenv("CORS_HEADERS", "*").split(",")
            exposed_headers = (
                os.getenv("CORS_EXPOSED_HEADERS", "").split(",")
                if os.getenv("CORS_EXPOSED_HEADERS")
                else []
            )
            credentials = os.getenv("CORS_CREDENTIALS", "false").lower() == "true"
            max_age = int(os.getenv("CORS_MAX_AGE", "3600"))

            # Add CORS middleware
            app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=credentials,
                allow_methods=methods,
                allow_headers=allowed_headers,
                expose_headers=exposed_headers,
                max_age=max_age,
            )

            return app

        return {}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Middleware error: {str(e)}")


# Middleware Group Dependency Functions


async def platform_auth_platform_auth_middleware_group_dependency(
    request: Request,
) -> Dict[str, Any]:
    """
    Dependency function for middleware group: platform_auth_platform_auth_middleware_group
    Executes all middlewares in the group in sequence
    """
    result = {}

    # Execute auth_package_middleware
    middleware_result = await auth_package_middleware(request)
    if isinstance(middleware_result, dict):
        result.update(middleware_result)
        # Store middleware variables in request.state for API handlers to access
        for key, value in middleware_result.items():
            setattr(request.state, key, value)

    return result


async def default_dependency(request: Request) -> Dict[str, Any]:
    """
    Dependency function for middleware group: default
    Executes all middlewares in the group in sequence
    """
    result = {}

    # Execute cors_middleware
    middleware_result = await cors_middleware(request)
    if isinstance(middleware_result, dict):
        result.update(middleware_result)
        # Store middleware variables in request.state for API handlers to access
        for key, value in middleware_result.items():
            setattr(request.state, key, value)

    return result
