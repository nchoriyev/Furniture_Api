from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError
from Fast.app.database import Session, ENGINE
from Fast.app.models import Country
from Fast.app.schemas import CountryCreate

country_router = APIRouter(prefix="/country", tags=["Country"])

session = Session(bind=ENGINE)


@country_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_country(country: CountryCreate):
    country_check = session.query(Country).filter(
        (Country.name == country.name)
    ).first()

    if country_check:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Country with this name or code already exists")

    # Create new country entry
    new_country = Country(
        name=country.name,
    )

    try:
        session.add(new_country)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database Error")

    return {"status": "success", "detail": "Country registered successfully"}
