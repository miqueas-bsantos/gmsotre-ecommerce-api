from datetime import datetime
from typing import List
from sqlalchemy                 import (Table, Numeric, Column, String, Integer, DateTime, Boolean, ForeignKey, func, between)
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm             import relationship
from os import environ
import model
from db import Base

association_sales = Table("TB_PRODUCTS_SALES", Base.metadata,
    Column("sale_id", Integer, ForeignKey("TB_SALES.id")),
    Column("product_id", Integer, ForeignKey("TB_PRODUCTS.id"))
)

class Delivery(Base):
    __tablename__ = 'TB_DELIVERY'
    id = Column(Integer, autoincrement=True, primary_key=True)
    from_store = Column(Integer, ForeignKey("TB_STORES.id"))
    to_address = Column(Integer, ForeignKey("TB_ADDRESS.id"))
    sale_id = Column(Integer, ForeignKey("TB_SALES.id"))
    price = Column(Numeric, nullable=False)
    company = Column(String(100), nullable=False)
    status = Column(String(30), nullable=False)
    createdAt = Column(DateTime)
    deliveryAt = Column(DateTime)

class Sales(Base):
    __tablename__ = 'TB_SALES'
    id = Column(Integer, autoincrement=True, primary_key=True)
    products = relationship("Product", secondary=association_sales, lazy="joined")
    # total = Column(Numeric, nullable=False)
    delivery = relationship("Delivery", lazy="joined")
    status = Column(String(30), nullable=False)
    createdAt = Column(DateTime)
    completedAt = Column(DateTime)
    user_id = Column(Integer, ForeignKey("TB_USERS.id"))
