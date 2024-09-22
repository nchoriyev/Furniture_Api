from fastapi import APIRouter, Depends, HTTPException, status
from Fast.app.database import ENGINE, Session
from Fast.app.models import Delivery, User
from Fast.app.schemas import DeliveryCreate, DeliveryResponse
from typing import List
from fastapi_jwt_auth import AuthJWT

delivery_router = APIRouter(prefix="/deliveries", tags=["Delivery"])

session = Session(bind=ENGINE)


@delivery_router.post("/", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
async def create_delivery(delivery: DeliveryCreate, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_delivery = Delivery(user_id=user.id, order_id=delivery.order_id, status=delivery.status)
    session.add(new_delivery)
    session.commit()
    session.refresh(new_delivery)

    return new_delivery


# Get only the deliveries of the logged-in user
@delivery_router.get("/", response_model=List[DeliveryResponse])
async def get_user_deliveries(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_deliveries = session.query(Delivery).filter(Delivery.user_id == user.id).all()
    return user_deliveries


# Get a specific delivery for the logged-in user
@delivery_router.get("/{delivery_id}", response_model=DeliveryResponse)
async def get_user_delivery(delivery_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    current_user = Authorize.get_jwt_subject()
    user = session.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    delivery = session.query(Delivery).filter(Delivery.id == delivery_id, Delivery.user_id == user.id).first()

    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")

    return delivery
