from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class ReportDetail(BaseModel):
    detailId: Optional[int] = 0
    clientCode: Optional[str] = ""
    shortName: Optional[str] = None
    storeCode: Optional[str] = None
    merchantCode: Optional[str] = None
    text: Optional[str] = None
    error: Optional[str] = None
    statusCode: Optional[str] = None
    fileDate: Optional[str] = None
    createdAt: Optional[datetime] = None
    endAt: Optional[datetime] = None
    isDone: Optional[bool] = False
    isRunning: Optional[bool] = False
    retrys: Optional[int] = 0
    # processId: Optional[int] = None
    # webhookId: Optional[int] = None  
    acquirer: Optional[str] = None

class DefaultResponseData(BaseModel):
    statusCode: Optional[int] = 200
    meta: Optional[dict] = {}
    messages: Optional[str] = None
    data: Optional[List]

class RequesProcess(BaseModel):
    merchantCode: str
    clientCode: str
    shortName: str
    storeCode: str
    files: List[str]

class Tags(BaseModel):
    id: Optional[int]
    tag: str

    class Config:
        orm_mode = True

class Image(BaseModel):
    id: Optional[int]
    path: str
    order: Optional[int]
    product_id: Optional[int]

    class Config:
        orm_mode = True    

class Sizes(BaseModel):
    id: Optional[int]
    size: str
    quantity: int
    
    class Config:
        orm_mode = True    

class Discount(BaseModel):
    id: Optional[int]
    start: str
    end: str
    value: float

    class Config:
        orm_mode = True  

### SubCategory Schemas ### 
class PostSchemaSubCategory(BaseModel):
    id: Optional[int]
    name: Optional[str]
    category_id: Optional[int]

class GetSchemaSubCategory(BaseModel):
    id: Optional[int]
    name: Optional[str]
    products: Optional[List]


class Category(BaseModel):
    id: Optional[int]
    name: Optional[str]
    order: Optional[int]
    # SubCategory: Optional[SubCategory]
    # products: Optional[List[Product]]

    # class Config:
    #     orm_mode = True 


class Product(BaseModel):
    id: Optional[int]
    code: Optional[str] = ""
    # imageUri: str
    imagesUriDetail: List[Image]
    title: str
    content: Optional[str]
    price: float
    currency: str
    sizes: List[Sizes]
    # quantity: int
    discount: List[Discount]
    subcategory: Optional[PostSchemaSubCategory]
    brand: str
    tags: List[Tags]
    isActive: bool
    plan: int

    class Config:
        orm_mode = True

