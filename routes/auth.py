import json
import traceback

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from services import auth

router = APIRouter()


class UsernameAndPassword(BaseModel):
    username: str
    password: str


class AuthenticationErrorResponse(BaseModel):
    message: str

def generate_random_auth():
    import random
    import string

    length = 10
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

@router.post("/auth/login", tags=["Authentication"])
def login(request: Request, response: Response, user_pass: UsernameAndPassword):
    try:
        print("Called login:", user_pass)
        user = auth.get_user_by_username(user_pass.username)
        if user is None or user.password != user_pass.password:
            response.status_code = 401
            return AuthenticationErrorResponse(message="Incorrect username or password")
        request.session["user"] = user.user_id
        request.session['access_token'] = generate_random_auth()
        res = {'user_id': user.user_id, 'username': user.username, 'access_token': request.session['access_token']}
        return res
    except:
        traceback.print_exc()


@router.post("/auth/logout", tags=["Authentication"])
def logout(request: Request):
    request.session.clear()
    return JSONResponse({"message": "logout successfully"}, status_code=200)


@router.get("/auth/user", tags=["Authentication"])
def get_current_user(request: Request):
    if "user" not in request.session:
        return JSONResponse({"message": "Request not authenticated"}, status_code=401)
    user_id = request.session["user"]
    user = auth.get_user_by_id(user_id)
    return user
