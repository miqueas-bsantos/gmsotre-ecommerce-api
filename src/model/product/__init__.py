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
    between,
)
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm             import relationship, session
from os import environ
from sqlalchemy.sql.expression import true
from sqlalchemy.sql.sqltypes import Numeric
from db import SessionLocal, engine, Base
import model
# from aws import S3
# from sqlalchemy_paginator import Paginator
from sqlalchemy.orm import load_only
from sqlalchemy.orm import defer
from sqlalchemy.orm.attributes import set_attribute
import boto3
from config import environ

association_tags = Table("TB_PRODUCTS_TAGS", Base.metadata,
    Column("tag_id", Integer, ForeignKey("TB_TAGS.id")),
    Column("product_id", Integer, ForeignKey("TB_PRODUCTS.id"))
)

association_discounts = Table("TB_PRODUCTS_DISCOUNTS", Base.metadata,
    Column("discounts_id", Integer, ForeignKey("TB_DISCOUNT.id")),
    Column("product_id", Integer, ForeignKey("TB_PRODUCTS.id"))
)

class ImagesDetail(Base):
    __tablename__ = "TB_IMAGES_S3"
    id = Column(Integer, autoincrement=True, primary_key=True)
    path = Column(String(255), nullable=True)
    product_id  = Column(Integer, ForeignKey('TB_PRODUCTS.id'))
    order = Column(Integer)

    def save_image(self) -> str:
        self.session = SessionLocal()
        message = "succefuly created!"
        id = 0
        try:
            product = self.session.query(Product).filter(Product.id==self.product_id).first()
            if product:
                self.session.add(self)
                self.session.commit()
                id = self.id
            else:
                message = "product not finded"
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return message, id

    def delete_image(self, uid: str, product_id: int) -> str:
        self.session = SessionLocal()
        message = "succefuly deleted!"
        try:
            delete = self.session.query(ImagesDetail)\
                                 .filter(
                                     ImagesDetail.path.like(f"%{uid}%"),
                                     ImagesDetail.product_id==product_id
                                 ).first()
            print(delete, uid, product_id)
            if delete:
                s3 = boto3.client('s3', region_name="us-east-1")
                s3.delete_object(
                    Bucket=environ["bucket_assets_images"],
                    Key=delete.path.split("/")[::-1][0],
                )
                # delete.delete(synchronize_session=False)
                # delete.delete()
                self.session.delete(delete)
                self.session.commit()
            else:
                message = "Image not finded"
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return message

    def get_images(self, product_id: int) -> str:
        self.session = SessionLocal()
        message = "succefuly finded!"
        image = None
        try:
            image = self.session.query(ImagesDetail)\
                                 .filter(
                                     ImagesDetail.product_id==product_id
                                 ).all()
            if image:
                pass
            else:
                message = "Image not finded"
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return message, image

class Sizes(Base):
    __tablename__ = "TB_SIZES"
    id = Column(Integer, autoincrement=True, primary_key=True)
    size = Column(String(3), nullable=True)
    quantity = Column(Integer, nullable=True)
    product_id  = Column(Integer, ForeignKey('TB_PRODUCTS.id'))

class Discount(Base):
    __tablename__ = "TB_DISCOUNT"
    id = Column(Integer, autoincrement=True, primary_key=True)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    value = Column(Numeric, nullable=False)
    products = relationship("Product", secondary=association_discounts, lazy="joined")

    @classmethod
    def upsert(cls, discounts: List["Discount"]):
        cls.session = SessionLocal()
        ids = []
        try:
            for discount in discounts:
                dbDiscount = cls.session.query(cls).filter(discount.id==cls.id).first()
                if discount.id and dbDiscount:
                    ids.append(dbDiscount.id)
                else: 
                    cls.session.add(discount)
                    cls.session.commit()
                    ids.append(discount.id)
            discounts = cls.session.query(cls).filter(cls.id.in_(ids)).all()
        except Exception as error:
            print(str(error))
        finally:
            cls.session.close()
            return discounts

class Category(Base):
    __tablename__ = "TB_CATEGORY"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(30), nullable=False)
    order = Column(Integer, nullable=False)
    subcategories = relationship("SubCategory", lazy="joined")

    def save_category(self) -> str:
        """Save self object in the database"""
        session = SessionLocal()
        text = "Sucelly saved!"
        try:
            session.add(self)
            session.commit()
        except Exception as error:
            print(str(error))
            text = str(error)
        finally:
            session.close()
            return text
            
    @classmethod
    def update_category(cls, category: str, order: int, id: int):
        """update the given object in the database"""
        session = SessionLocal()
        text = "Successfully update!"
        try:
            object = session.query(cls).filter(cls.id==id).first()
            object.name = category
            object.order = order
            session.commit()
        except Exception as error:
            print(str(error))
            text = str(error)
        finally:
            session.close()
            return text

    @classmethod
    def delete_category(cls, id: int):
        """update the given object in the database"""
        session = SessionLocal()
        text = "Successfully delete!"
        try:
            object = session.query(cls).filter(cls.id==id).first()
            if object and len(object.subcategories) and len(object.subcategories.products):
                text= "This operation can't be complete, because there is products in this category!"
            else:
                session.delete(object)
                session.commit()
        except Exception as error:
            print(str(error))
            text = str(error)
        finally:
            session.close()
            return text

    @classmethod
    def find_all_category(cls):
        """update the given object in the database"""
        session = SessionLocal()
        results = []
        try:
            results = session.query(cls).filter(cls.name!='NÃO IDENT.').all()
        except Exception as error:
            print(str(error))
        finally:
            session.close()
            return results
    
    @classmethod
    def find_category(cls, id: int)  -> "Category":
        """update the given object in the database"""
        session = SessionLocal()
        results = {}
        try:
            results = session.query(cls).filter(cls.id==id).first()
        except Exception as error:
            print(str(error))
        finally:
            session.close()
            return results

class SubCategory(Base):
    __tablename__ = "TB_SUBCATEGORY"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(String(30), nullable=False)
    products = relationship("Product", lazy="joined")
    category_id = Column(Integer, ForeignKey('TB_CATEGORY.id'), nullable=False)
    
    def save_subcategory(self) -> str:
        """Save self object in the database"""
        session = SessionLocal()
        text = "Sucelly saved!"
        try:
            session.add(self)
            session.commit()
        except Exception as error:
            print(str(error))
            text = str(error)
        finally:
            session.close()
            return text
            
    @classmethod
    def update_subcategory(cls, name: str, id: int):
        """update the given object in the database"""
        session = SessionLocal()
        text = "Successfully update!"
        try:
            object = session.query(cls).filter(cls.id==id).first()
            object.name = name
            session.commit()
        except Exception as error:
            print(str(error))
            text = str(error)
        finally:
            session.close()
            return text

    @classmethod
    def delete_subcategory(cls, id: int):
        """delete the given object id in the database"""
        session = SessionLocal()
        text = "Successfully delete!"
        try:
            object = session.query(cls).filter(cls.id==id).first()
            if object and len(object.products):
                text= "This operation can't be complete, because there is products in this subcategory!"
            else:
                session.delete(object)
                session.commit()
        except Exception as error:
            print(str(error))
            text = str(error)
        finally:
            session.close()
            return text

    @classmethod
    def find_all_subcategory(cls):
        """retrieve all objects in the database"""
        session = SessionLocal()
        results = []
        try:
            results = session.query(cls).all()
        except Exception as error:
            print(str(error))
        finally:
            session.close()
            return results
    
    @classmethod
    def find_subcategory_by_id(cls, id: int)  -> "Category":
        """find the given object id in the database"""
        session = SessionLocal()
        results = {}
        try:
            results = session.query(cls).filter(cls.id==id).first()
        except Exception as error:
            print(str(error))
        finally:
            session.close()
            return results

    @classmethod
    def find_subcategory_by_category_id(cls, id: int)  -> "Category":
        """find the given object category id in the database"""
        session = SessionLocal()
        results = []
        try:
            results = session.query(cls).filter(cls.category_id==id).all()
        except Exception as error:
            print(str(error))
        finally:
            session.close()
            return results

class Tags(Base):
    __tablename__ = "TB_TAGS"
    id = Column(Integer, autoincrement=True, primary_key=True)
    tag = Column(String(30), nullable=False)
    products = relationship("Product", secondary=association_tags, lazy="joined")

    @classmethod
    def upsert(cls, tags: List["Tags"], session):
        cls.session = session
        instances = []
        try:
            for tag in tags:
                dbTag = cls.session.query(cls).filter(Tags.tag.ilike("%"+tag.tag+"%")).first()
                if tag.id and dbTag:
                    instances.append(dbTag.id)
                else: 
                    cls.session.add(tag)
                    # cls.session.commit()
                    print("criando")
                    instances.append(tag.id)
        except Exception as error:
            print(str(error))
        finally:
            print(instances)
            return cls.session.query(cls).filter(cls.id.in_(instances)).all()

class Product(Base):
    __tablename__ = "TB_PRODUCTS"
    id = Column(Integer, autoincrement=True, primary_key=True)
    code = Column(String(255), nullable=True)
    # imageUri = Column(String(255), nullable=False)
    imagesUriDetail = relationship("ImagesDetail", lazy="joined", cascade = "all, delete, delete-orphan")
    title = Column(String(255), nullable=False)
    content = Column(String(500), nullable=True)
    price = Column(Numeric, nullable=False)
    currency = Column(String(10), nullable=False)
    sizes = relationship("Sizes", lazy="joined", cascade = "all, delete, delete-orphan")
    # quantity = Column(Integer, nullable=False)
    # currentQuantity = Column(Integer, nullable=False)
    discount = relationship("Discount", secondary=association_discounts, lazy="joined")
    brand = Column(String(30), nullable=False)
    tags = relationship("Tags", secondary=association_tags, lazy="joined")
    subcategory_id = Column(Integer, ForeignKey('TB_SUBCATEGORY.id'), nullable=True)
    subcategory = relationship("SubCategory", lazy="joined")
    owner_id = Column(Integer, ForeignKey('TB_STORES.id'))
    isActive = Column(Boolean, default=False)
    plan = Column(Integer, nullable=False)
    # imagesUriDetail_id = Column(Integer-p, ForeignKey('TB_IMAGES_S3.id'))
    # sizes_id = Column(Integer, ForeignKey('TB_SIZES.id'))
    # tags_id = Column(Integer, ForeignKey('TB_TAGS.id'))

    def create_tables(self):
        # for table in [ImagesDetail, Sizes, Discount, Tags, Product]:
        #     try:
        #         table.__table__.drop(engine)
        #     except Exception as error:
        #         print(error)
        Base.metadata.create_all(bind=engine)

    def insert_product(self, tags, discounts) -> str:
        # self.create_tables()
        self.session = SessionLocal()
        print("passou0")
        text = "Produto cadastrado com sucesso!"
        try:
            if self.subcategory.id:
                self.subcategory = self.session.query(SubCategory).filter(SubCategory.id==self.subcategory.id).first()
                if not hasattr(self.subcategory, "name"):
                    text = "Invalid category id!"
            self.session.add(self)
            if discounts:
                self.discount = Discount.upsert(discounts)
            if tags:
                self.tags = Tags.upsert(tags, self.session)
            self.session.commit()
        except Exception as error:
            print(str(error))
            text = str(text)
        finally:
            self.session.close()
            return text

    def update_product(self, product) -> "Product":
        self.session = SessionLocal()
        results = {}
        try:
            results = self.session.query(Product).filter(Product.id == product["id"]).first()
            # first level
            for key, value in product.items():
                if not isinstance(value, list):
                    if key == 'subcategory':
                        results.subcategory = self.session.query(SubCategory).filter(SubCategory.id==product['subcategory']['id']).first()
                    else:    
                        set_attribute(results, key, value)
                else:
                    # second level images, sizes...
                    item = getattr(results, key)
                    for i in item:
                        find_related = next(filter(lambda x: int(x["id"])==i.id, value))
                        if find_related:
                            for key2, value2 in find_related.items():
                                if key2 == 'start' or key2 == 'end':
                                    value2 = datetime.fromisoformat(value2)
                                set_attribute(i, key2, value2)
                
            self.session.commit()
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return {}

    def get_products_by_id(self, id: int) -> "Product":
        self.create_tables()
        self.session = SessionLocal()
        products = []
        try:
            products = self.session.query(Product)\
                                   .options(
                                       defer(Product.owner_id), 
                                       defer(Product.subcategory_id)
                                    ).filter(Product.id==id)
            products = products.first()
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return products

    def get_products_by_category_id(self, id: str, sizes: list, tags: list, price: float) -> "Product":
        self.create_tables()
        self.session = SessionLocal()
        products = []
        try:
            products = self.session.query(Product)\
                                   .options(
                                       defer(Product.owner_id), 
                                       defer(Product.subcategory_id)
                                    ).select_from(Product)\
                                    .join(SubCategory)\
                                    .join(Category)\
                                    .filter(Category.name==id)
            if len(sizes):
                products = products.join(Sizes).filter(Sizes.size.in_(sizes), Sizes.quantity > 0)
            if len(tags):
                products = products.join(association_tags).join(Tags).filter(Tags.tag.in_(tags))
            if price > 0:
                products = products.filter(Product.price <= price)
            products = products.all()                              
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return products

    def get_products_by_subcategory_id(self, id: str, sizes: list, tags: list, price: float) -> "Product":
        self.create_tables()
        self.session = SessionLocal()
        products = []
        try:
            products = self.session.query(Product)\
                                   .options(
                                       defer(Product.owner_id), 
                                       defer(Product.subcategory_id)
                                    ).select_from(Product)\
                                    .join(SubCategory)\
                                    .filter(SubCategory.name==id)
            if len(sizes):
                products = products.join(Sizes).filter(Sizes.size.in_(sizes))
            if len(tags):
                products = products.join(association_tags).join(Tags).filter(Tags.tag.in_(tags))
            if price > 0:
                products = products.filter(Product.price <= price)                
            products = products.all()                                 
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return products

    def get_products(self, category: str) -> List["Product"]:
        self.create_tables()
        self.session = SessionLocal()
        products = []
        try:
            products = self.session.query(Product).options(defer(Product.owner_id), defer(Product.subcategory_id))
            if category.upper() != 'ALL':
                products = products.join(SubCategory, SubCategory.id == Product.subcategory_id)\
                                   .join(Category, SubCategory.category_id == Category.id)\
                                   .filter(Category.name==category)

            products = products.all()
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return products

    def get_products_home(self, category: str) -> List["Product"]:
        self.create_tables()
        self.session = SessionLocal()
        products = []
        try:
            products = self.session.query(Product).options(defer(Product.owner_id), defer(Product.subcategory_id))
            if category.upper() != 'ALL':
                products = products.join(SubCategory, SubCategory.id == Product.subcategory_id)\
                                   .join(Category, SubCategory.category_id == Category.id)\
                                   .filter(Category.name==category)

            products = products.all()
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return products

    def delete(self, id: int) -> List["Product"]:
        self.create_tables()
        self.session = SessionLocal()
        result = 0
        try:
            product =  self.session.query(Product).filter(Product.id==id).first()
            result = self.session.delete(product)
            self.session.commit()
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return "Deleted!" if result else "not found!"