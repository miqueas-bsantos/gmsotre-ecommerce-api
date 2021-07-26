from datetime import datetime
from typing import Optional
from fastapi.exceptions import HTTPException
from fastapi import APIRouter, status
from model import Acquirer as AcquirerModel, Schemas
from typing import List

router = APIRouter()

@router.get("/acquirers/reports/download", description="Get all acquirers download files report available")
async def get_acquires_report(start_date: str, end_date: str):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["data"], response["mapKeys"] = AcquirerModel('ALL')\
                                .get_reports_download(
                                    start_date=datetime.fromisoformat(f"{start_date[:10]}T00:00:00"), 
                                    end_date=datetime.fromisoformat(f"{end_date[:10]}T23:59:59")
                                )
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )

@router.put("/acquirers/reports/download", description="Reprocess selected acquirers files")
async def reprocess_acquires_report(files: List[int], status: str):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        acquirer_model = AcquirerModel('ALL')
        response["data"], response["mapKeys"] = acquirer_model.reprocess_files(files, status)
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )

@router.post("/acquirers/reports/download/detail", 
            description="Get details acquirers download files report available",
            response_model=Schemas.DefaultResponseData,
            tags=["Reports"])
async def get_acquires_report(start_date: str, end_date, acquirer: str, page: int = 1, pageSize: int = 10, filters: Optional[list] = []):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": "",
        "meta": {}
    }
    # print(filters)
    try:
        response["data"], response["mapKeys"], response["meta"] = AcquirerModel(acquirer).get_reports_download_detail(
                                    start_date=datetime.fromisoformat(f"{start_date[:10]}T00:00:00"), 
                                    end_date=datetime.fromisoformat(f"{end_date[:10]}T23:59:59"),
                                    acquirer=acquirer,
                                    filters=filters,
                                    page=page,
                                    pageSize=pageSize
                                )
        # print(response["meta"] )
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )

@router.get("/acquirers/reports/download/count", 
            description="Get acquirers download count report")
async def get_acquires_report_count(start_date: str, end_date: str):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["data"], response["mapKeys"] = AcquirerModel('ALL').get_acquirers_count(
                                    start_date=datetime.fromisoformat(f"{start_date[:10]}T00:00:00"), 
                                    end_date=datetime.fromisoformat(f"{end_date[:10]}T23:59:59")
                                )
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )

@router.get("/acquirers/reports/download/prevision", 
            description="Get all acquirers download history prevision vs current report")
async def get_acquires_prevision_vs_current_report(start_date: str, end_date: str):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["data"], response["mapKeys"] = AcquirerModel('ALL').get_prevision_vs_current(
                                    start_date=datetime.fromisoformat(f"{start_date[:10]}T00:00:00"), 
                                    end_date=datetime.fromisoformat(f"{end_date[:10]}T23:59:59")
                                )
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )

@router.get("/acquirers/reports/download/establishments/{acquirer}", 
            description="Get all merchants numbers and clientCode")
async def get_acquires_available_merchant_numbers(acquirer: str):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["data"], response["mapKeys"] = AcquirerModel('ALL').load_merchants(acquirer)
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )

@router.get("/acquirers/reports/download/availableFiles/{acquirer}", 
            description="Get all acquirers availableFiles to download")
async def get_available_files(acquirer: str, start_date: str, end_date: str, merchant_code: str):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["data"], response["mapKeys"] = AcquirerModel('ALL').get_available_files(
                                                                        acquirer=acquirer,
                                                                        start_date=datetime.fromisoformat(f"{start_date[:10]}T00:00:00"), 
                                                                        end_date=datetime.fromisoformat(f"{end_date[:10]}T23:59:59"),
                                                                        merchant_code=merchant_code
                                                                    )
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )

@router.post("/acquirers/reports/download/reprocess/{acquirer}", 
            description="Reprocess all acquirers seleted files",
            tags=["Recovery files"])
async def reprocess_available_files(files: Schemas.RequesProcess, acquirer: str):
    response = {
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["messages"], response["mapKeys"] = AcquirerModel('ALL').reprocess(files=files, acquirer=acquirer)
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )

@router.post("/acquirers/reports/download/detail/filters", 
            description="Reprocess all acquirers seleted files",
            tags=["Reports"])
async def get_available_reports_filters(column: str, start_date: str, end_date, filters: Optional[list] = []):
    # print(filters)
    response = {
        "meta": {},
        "statusCode": 200,
        "data": [],
        "messages": ""
    }
    try:
        response["meta"], response["data"], response["statusCode"] = AcquirerModel('ALL').get_names(
                                    start_date=datetime.fromisoformat(f"{start_date[:10]}T00:00:00"), 
                                    end_date=datetime.fromisoformat(f"{end_date[:10]}T23:59:59"),
                                    filters=filters,
                                    column=column
                                    )
        return response
    except Exception as errors:
        print(str(errors))
        response["messages"] = str(errors)
        response["statusCode"]=status.HTTP_500_INTERNAL_SERVER_ERROR
        raise HTTPException(
            status_code=500,
            detail=response
        )