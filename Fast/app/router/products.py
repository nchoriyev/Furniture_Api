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


def get_current_user(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = session.query(User).filter(User.username == Authorize.get_jwt_subject()).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return current_user


@router.post("/create", response_model=ProductRegister)
async def create_product(
        product: ProductRegister,
        Authorize: AuthJWT = Depends()
):
    Authorize.jwt_required()
    current_user_id = get_current_user(Authorize)

    user = session.query(User).filter(User.id == current_user_id).first()

    if not user or user.status != UserStatus.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    new_product = Product(
        name=product.name,
        description=product.description,
        image=product.image,
        price1=product.price1,
        price2=product.price2,
        material=product.material,
        count=product.count,
        slug=product.slug
    )
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

    current_user_username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == current_user_username).first()

    if current_user.status != UserStatus.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You do not have permission to perform this action")

    user_to_update = session.query(User).filter(User.id == user_id).first()

    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_to_update.status = new_status
    session.commit()

    return {"status_code": 200,
            "detail": f"User {user_to_update.username}'s status has been changed to {new_status.value}"}


@router.get("/search/{slug}", response_model=ProductRegister)
async def get_product_by_slug(slug: str, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()

    product = session.query(Product).filter(Product.slug == slug).first()

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return product
