from datetime import datetime
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status
# from model import Acquirer as AcquirerModel, Schemas
import uuid

from model import (
    CategoryModel,
    ProductModel,
    Schemas
)

router = APIRouter()

@router.get("/products/category", 
            description="Get all categories avaibles", 
            tags=["Category"], 
            response_model=Schemas.DefaultResponseData
)
async def find_all_categories():
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["data"] = CategoryModel().find_all_category() 
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.get("/products/category/{id}", description="Get the given category id", tags=["Product Category"])
async def find_category_by_id(id: str, sizes: Optional[str]= '', tags: Optional[str] = '', price: Optional[float] = 0):
    response = {
        "statusCode": 200,
        "data": {},
        "messages": ""
    }
    try:
        sizes = sizes.split(',') if sizes != '' else []
        tags = tags.split(',') if tags != '' else []
        
        response["data"] = ProductModel().get_products_by_category_id(id=id, sizes=sizes, tags=tags, price=price) 
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.post("/products/category", description="Save the given category", tags=["Category"])
async def create_category(category: Schemas.Category):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["messages"] = CategoryModel(**category.dict()).save_category()
        response["data"] = CategoryModel().find_all_category()
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.put("/products/category", description="Update the given category", tags=["Category"])
async def update_category(category: Schemas.Category):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["messages"] = CategoryModel().update_category(id=category.id, category=category.name, order=category.order)
        response["data"] = CategoryModel().find_all_category()
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.delete("/products/category/{id}", description="Delete the given category id", tags=["Category"])
async def delete_category(id: int):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["messages"] = CategoryModel().delete_category(id)
        response["data"] = CategoryModel().find_all_category()
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )