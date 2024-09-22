from fastapi import FastAPI
from uvicorn import run
from .router import auth
from .router import products
from .router import country
from fastapi_jwt_auth import AuthJWT
from Fast.app.schemas import Settings

app = FastAPI()
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(country.country_router)


@AuthJWT.load_config
def get_config():
    return Settings()


@app.get("/")
async def root():
    return {"Message": "Assalomu Aleykum Asosiy Sahifaga xush kelibsiz!"}

