from datetime import datetime
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status
# from model import Acquirer as AcquirerModel, Schemas
import uuid

from model import (
    SubCategoryModel,
    ProductModel,
    Schemas
)

router = APIRouter()

@router.get("/products/category/subcategory", 
            description="Get all subcategories avaibles", 
            tags=["SubCategory"], 
            response_model=Schemas.DefaultResponseData
)
async def find_all_subcategory():
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["data"] = SubCategoryModel().find_all_subcategory() 
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.get("/products/category/subcategory/{id}", description="Get the given subcategory id", tags=["Product SubCategory"])
async def find_subcategory_by_id(id: str, sizes: Optional[str]= '', tags: Optional[str] = '', price: Optional[float] = 0):
    response = {
        "statusCode": 200,
        "data": {},
        "messages": ""
    }
    try:
        sizes = sizes.split(',') if sizes != '' else []
        tags = tags.split(',') if tags != '' else []        
        response["data"] = ProductModel().get_products_by_subcategory_id(id=id, sizes=sizes, tags=tags, price=price) 
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.post("/products/category/subcategory", description="Save the given subcategory", tags=["SubCategory"])
async def create_subcategory(subcategory: Schemas.PostSchemaSubCategory):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        sub = SubCategoryModel(**subcategory.dict())
        response["messages"] = sub.save_subcategory()
        response["data"] = sub.find_subcategory_by_category_id(id=subcategory.category_id)
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.put("/products/category/subcategory", description="Update the given subcategory", tags=["SubCategory"])
async def update_subcategory(subcategory: Schemas.PostSchemaSubCategory):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        sub = SubCategoryModel()
        response["messages"] = sub.update_subcategory(id=subcategory.id, name=subcategory.name)
        response["data"] = sub.find_subcategory_by_category_id(id=subcategory.category_id)
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.delete("/products/category/subcategory/{id}/{category_id}", description="Delete the given subcategory id", tags=["SubCategory"])
async def delete_subcategory(id: int, category_id: int):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        sub = SubCategoryModel()
        response["messages"] = sub.delete_subcategory(id)
        response["data"] = sub.find_subcategory_by_category_id(id=category_id)
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )