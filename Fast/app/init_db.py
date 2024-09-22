from .database import Base, ENGINE
from .models import Country, City, Address, Product, User, Order, Delivery, Contact


def migrate():
    Base.metadata.create_all(bind=ENGINE)

