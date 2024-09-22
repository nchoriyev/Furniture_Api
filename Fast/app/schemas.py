from typing import Optional
from pydantic import BaseModel


class Settings(BaseModel):
    authjwt_secret_key = '63939fbc26ba82006f69c806dbf8935c223e35eed8e289c2a85033321454c339'


class UserLogin(BaseModel):
    username: Optional[str]
    password: Optional[str]


class UserRegister(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]


class ProductUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    material: Optional[str]
    price1: Optional[float]
    price2: Optional[float]
    status: Optional[bool]
    featured: Optional[bool]
    country_id: Optional[int]
    count: Optional[int]
    slug: Optional[str]


class ProductRegister(BaseModel):
    name: Optional[str]
    description: Optional[str]
    material: Optional[str]
    price1: Optional[float]
    price2: Optional[float]
    country_id: Optional[int]
    count: Optional[int]
    slug: Optional[str]


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: Optional[str]


class UserPartialUpdate(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]


class CountryCreate(BaseModel):
    name: Optional[str]
