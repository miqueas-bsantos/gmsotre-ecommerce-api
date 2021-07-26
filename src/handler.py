from fastapi import FastAPI
from routes import (
    ProductRoutes,
    CategoryRoutes,
    SubCategoryRoutes
)
from fastapi.middleware.cors import CORSMiddleware
# Mangum is an adapter for using ASGI applications with 
# AWS Lambda & API Gateway. It is intended to provide
# an easy-to-use, configurable wrapper for any ASGI 
# application deployed in an AWS Lambda function to 
# handle API Gateway requests and responses.
from mangum import Mangum

app = FastAPI(docs_url="/concilcore/files/docs", redoc_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(SubCategoryRoutes)
app.include_router(CategoryRoutes)
app.include_router(ProductRoutes)
gm_store = Mangum(app)
# acquirers_downloads_reports = Mangum(app)
    
# DB_CONNECTION = Postgres(
#     host=environ.get('HOST', 'concildevblackbox.c0rzxyeauhjq.us-east-1.rds.amazonaws.com'),
#     database=environ.get('DATABASE', 'concildevblackboxdatabase'),
#     user=environ.get('USER', 'awsuser'),
#     password=environ.get('PASSWORD', 'Ox!g3n!0'),
#     port=environ.get('PORT', 5432)
# )

# def acquirers_downloads_reports(event, context):
#     response = {
#         "body": {},
#         "statusCode": 200
#     }
#     start_date = event["queryStringParameters"]["start_date"]
#     end_date = event["queryStringParameters"]["end_date"]
#     try:
#         files = Acquirer(DB_CONNECTION.create_session())
#         response["body"] = json.dumps(files.get_reports_download(acquirer='ADYEN', start_date=datetime(2020, 1, 1), end_date=datetime(2021, 4, 1)), indent=4)
#     except Exception as error:
#         print(error)
#         response = {
#             "statusCode": 500,
#             "body": json.dumps({"message": str(error)})
#         }
#     finally:
#         return response

# if __name__ == '__main__':
#     acquirers_downloads_reports()