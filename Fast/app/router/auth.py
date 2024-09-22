import datetime
from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash
from Fast.app.database import Session, ENGINE
from Fast.app.schemas import UserLogin, UserRegister, UserUpdate, UserPartialUpdate
from Fast.app.models import User
from fastapi_jwt_auth import AuthJWT

router = APIRouter(prefix="/identify", tags=["Auth"])

# Initialize the session
session = Session(bind=ENGINE)

# User login endpoint
@router.post("/login")
async def login(request: UserLogin, authorization: AuthJWT = Depends()):
    check_user = session.query(User).filter(User.username == request.username).first()
    if check_user and check_password_hash(check_user.password, request.password):
        access_token = authorization.create_access_token(subject=request.username,
                                                         expires_time=datetime.timedelta(minutes=50))
        refresh_token = authorization.create_refresh_token(subject=request.username,
                                                           expires_time=datetime.timedelta(days=1))
        response = {
            "status_code": 200,
            "detail": "Login successful",
            'access_token': access_token,
            'refresh_token': refresh_token
        }
        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect password or username")

@router.post("/register")
async def register(request: UserRegister):
    user_check = session.query(User).filter(
        or_(
            User.username == request.username,
            User.email == request.email
        )
    ).first()
    if user_check is None:
        response = {
            "status_code": 200,
            "detail": "Register Successful"
        }
        data = User(
            first_name=request.first_name,
            last_name=request.last_name,
            username=request.username,
            email=request.email,
            password=generate_password_hash(request.password)
        )
        session.add(data)
        session.commit()

        return jsonable_encoder(response)
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User already exists")

# Get all users
@router.get("/users")
async def get_users():
    users = session.query(User).all()
    return jsonable_encoder(users)

# Verify token
@router.get("/token/verify")
def verify_token(Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token is expired or invalid")

    return {"status": "Token is valid"}

# Update user details completely (PUT)
@router.put("/users/{user_id}")
async def update_user(user_id: int, user_data: UserUpdate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.first_name = user_data.first_name
    user.last_name = user_data.last_name
    user.username = user_data.username
    user.email = user_data.email
    if user_data.password:
        user.password = generate_password_hash(user_data.password)

    session.commit()
    return jsonable_encoder(user)

# Update specific user fields (PATCH)
@router.patch("/users/{user_id}")
async def partial_update_user(user_id: int, user_data: UserPartialUpdate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user = session.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_data.first_name:
        user.first_name = user_data.first_name
    if user_data.last_name:
        user.last_name = user_data.last_name
    if user_data.username:
        user.username = user_data.username
    if user_data.email:
        user.email = user_data.email
    if user_data.password:
        user.password = generate_password_hash(user_data.password)

    session.commit()
    return jsonable_encoder(user)
