from datetime import datetime
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status, File, UploadFile, Header
# from model import Acquirer as AcquirerModel, Schemas
import uuid

from model import (
    ProductModel, 
    SizeModel,
    SubCategoryModel, 
    TagModel,
    DiscountModel,
    ImageModel,
    Schemas
)
from typing import List
import json
import boto3
import base64
from config import environ

router = APIRouter()

@router.get("/products", description="Get all product avaibles by category", tags=["Product"])
async def get_products(category: str, order_by: Optional[str]):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["data"] = ProductModel().get_products(category=category) 
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.post("/products", description="Create a product", tags=["Product"])
async def create_products(product: Schemas.Product):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    # print(json.dumps(product.dict(), indent=4))
    discount = False
    tags = False
    try:
        # product = product.dict()
        if product.discount:
            discount = [DiscountModel(id=discount.dict()["id"],
                                        start=datetime.fromisoformat(discount.dict()["start"]),
                                        end=datetime.fromisoformat(discount.dict()["end"]),
                                        value=discount.dict()["value"]) for discount in product.discount]
        if product.tags:
            tags = [TagModel(**tag.dict()) for tag in product.tags]
        if product.imagesUriDetail:
            images = [ImageModel(**image.dict()) for image in product.imagesUriDetail]
            product.imagesUriDetail = images
        if product.sizes:
            sizes = [SizeModel(**size.dict()) for size in product.sizes]
            product.sizes = sizes
        if product.subcategory:
            product.subcategory = SubCategoryModel(**product.subcategory.dict())
        productDb = ProductModel(**product.dict())
        productDb.tags = []
        productDb.discount = []
        response["messages"] = productDb.insert_product(tags=tags, discounts=discount)
        response["data"] = productDb.get_products("all")
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.put("/products", description="Update a product", tags=["Product"])
async def update_products(product: Schemas.Product):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    print(json.dumps(product.dict(), indent=4))
    try:

        productDb = ProductModel()
        productDb.update_product(product.dict())
        response['data'] = productDb.get_products('all')
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.delete("/products/{id}", description="Delete a product", tags=["Product"])
async def delete_product(id: int):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:

        productDb = ProductModel()
        response['messages'] = productDb.delete(id)
        response['data'] = productDb.get_products('all')
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.get("/products/{id}", description="Get a product by id", tags=["Product"])
async def get_product_by_id(id: int):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:

        productDb = ProductModel()
        response['messages'] = ""
        response['data'] = productDb.get_products_by_id(id)
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.post("/products/images", description="Update a product image")
async def create_upload_file(file: UploadFile = File("dasd"), Uid: str = Header(None), productId: int = Header(None)):
    response = {
        "statusCode": 200,
        "data": {},
        "messages": ""
    }
    
    try:
        s3 = boto3.client('s3', region_name="us-east-1")
        filename = f"{Uid}.{file.content_type.split('/')[1]}"
        print(productId)
        image = ImageModel(
                product_id=productId, 
                path = f'https://{environ["bucket_assets_images"]}.s3.amazonaws.com/{filename}'
            )
        message, id = image.save_image()
        contents = await file.read()
        s3.put_object(
                Body=contents,
                Bucket = environ["bucket_assets_images"],
                Key = filename
            )
        response["data"] = {
                "id": id,
                "uid": Uid,
                "name": filename,
                "status": 'done',
                "url": image.path,            
        }
        response["messages"] = message
        print({"file_size": file.filename})
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.delete("/products/images/{product_id}/{uid}", description="Delete a product image relationship")
async def delete_image_relationship_file_image(uid: str, product_id: int):
    response = {
        "statusCode": 200,
        "data": {},
        "messages": ""
    }
    
    try:
        response["messages"] = ImageModel().delete_image(uid, product_id)
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )

@router.get("/products/images/{product_id}", description="Get a product image relationship")
async def get_image_relationship_file_image(product_id: int):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    
    try:
        response["messages"], images = ImageModel().get_images(product_id)
        if images:
            response["data"] = [
                {
                    "url": image.path,
                    "path": image.path,
                    "uid": image.path.split("/")[::-1][0].split(".")[0],
                    "id": image.id,
                    "product_id": image.product_id,
                    "order": image.order
                } for image in images
            ]
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=response["statusCode"],
            detail=response
        )
