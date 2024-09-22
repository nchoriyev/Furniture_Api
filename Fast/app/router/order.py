from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .database import ENGINE, Session
from .models import Order, User
from .schemas import OrderCreate, OrderResponse
from typing import List
from fastapi_jwt_auth import AuthJWT  # For token authentication

order_router = APIRouter(prefix="/orders", tags=["Order"])

# Create a database session
session = Session(bind=ENGINE)


# Create a new order
@order_router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()  # Get current user's username from the token
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_order = Order(user_id=user.id, product_id=order.product_id, quantity=order.quantity)
    session.add(new_order)
    session.commit()
    session.refresh(new_order)

    return new_order


@order_router.get("/", response_model=List[OrderResponse])
async def get_user_orders(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_orders = session.query(Order).filter(Order.user_id == user.id).all()
    return user_orders


@order_router.get("/{order_id}", response_model=OrderResponse)
async def get_user_order(order_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    order = session.query(Order).filter(Order.id == order_id, Order.user_id == user.id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order
