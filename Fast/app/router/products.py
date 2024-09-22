import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from Fast.app.database import ENGINE
from Fast.app.models import Product, UserStatus, User
from Fast.app.schemas import ProductRegister, ProductUpdate
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import JSONResponse

# Initialize a session directly with the engine
session = Session(bind=ENGINE)

router = APIRouter(prefix="/products", tags=["Products"])


# Helper function to get the current user from the JWT token
def get_current_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()  # Require a valid token from cookies
    current_user = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return current_user


# Only admin can create a product
@router.post("/create", response_model=ProductRegister)
async def create_product(product: ProductRegister, Authorize: AuthJWT = Depends()):
    current_user = get_current_user(Authorize)
    if current_user.status != UserStatus.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    new_product = Product(**product.dict())
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product


# Only admin can update a product
@router.put("/update/{product_id}", response_model=ProductUpdate)
async def update_product(product_id: int, product: ProductUpdate, Authorize: AuthJWT = Depends()):
    current_user = get_current_user(Authorize)
    if current_user.status != UserStatus.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    existing_product = session.query(Product).filter(Product.id == product_id).first()
    if not existing_product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    for key, value in product.dict().items():
        setattr(existing_product, key, value)

    session.commit()
    session.refresh(existing_product)
    return existing_product


# Only admin can delete a product
@router.delete("/delete/{product_id}")
async def delete_product(product_id: int, Authorize: AuthJWT = Depends()):
    current_user = get_current_user(Authorize)
    if current_user.status != UserStatus.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    product = session.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    session.delete(product)
    session.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"detail": "Product deleted"})


# Any logged-in user can view products
@router.get("/", response_model=list[ProductRegister])
async def get_products(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    products = session.query(Product).all()
    return products


@router.put("/change-status/{user_id}")
async def change_user_status(user_id: int, new_status: UserStatus, Authorize: AuthJWT = Depends()):
    # Require valid JWT token
    Authorize.jwt_required()

    # Get the current logged-in user
    current_user_username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == current_user_username).first()

    # Ensure that the current user is an admin
    if current_user.status != UserStatus.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action")

    # Find the user whose status needs to be updated
    user_to_update = session.query(User).filter(User.id == user_id).first()

    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update the user's status
    user_to_update.status = new_status
    session.commit()

    return {"status_code": 200,
            "detail": f"User {user_to_update.username}'s status has been changed to {new_status.value}"}
