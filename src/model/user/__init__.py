from datetime import datetime
from typing import List
from sqlalchemy import (
    Table,
    Column, 
    String, 
    Integer, 
    DateTime, 
    Boolean, 
    ForeignKey, 
    func, 
    between
)
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm             import relationship
from os import environ
import model
from db import Base


# association_tags = Table("tb_products_s", Base.metadata,
#     Column("tag_id", Integer, ForeignKey("TB_TAGS.id")),
#     Column("product_id", Integer, ForeignKey("TB_PRODUCTS.id"))
# )

class Store(Base):
    __tablename__ = 'TB_STORES'
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(150), nullable=False)
    phone = Column(String(30), nullable=False)
    cnpj = Column(String(30), nullable=False)
    email = Column(String(100), nullable=False)
    users = relationship("User", lazy="joined")
    createdAt = Column(DateTime)
    address = relationship("Address", lazy="joined")
    products = relationship("Product", lazy="joined")

class User(Base):
    __tablename__ = 'TB_USERS'
    id = Column(Integer, autoincrement=True, primary_key=True)
    firstName = Column(String(50), nullable=False)
    lastName = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(30), nullable=False)
    cpf = Column(String(15), nullable=False)
    scope = Column(String(30), nullable=False)
    createdAt = Column(DateTime)
    birth = Column(DateTime)
    store_id  = Column(Integer, ForeignKey('TB_STORES.id'))
    # users = relationship("User", lazy="joined")
    address = relationship("Address", lazy="joined")
    sales = relationship("Sales", lazy="joined")


class Address(Base):
    __tablename__ = 'TB_ADDRESS'
    id = Column(Integer, autoincrement=True, primary_key=True)
    number = Column(Integer, nullable=False)
    street = Column(String(150), nullable=False)
    city = Column(String(50), nullable=False)
    state = Column(String(5), nullable=False)
    zipcode = Column(String(10), nullable=False)
    complement = Column(String(150), nullable=True)
    createdAt = Column(DateTime)
    store_id  = Column(Integer, ForeignKey('TB_STORES.id'))
    user_id  = Column(Integer, ForeignKey('TB_USERS.id'))
