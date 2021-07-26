from datetime import datetime
from typing import List, Dict
from sqlalchemy                 import (Column, String, Integer, DateTime, Boolean, ForeignKey, func, between)
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm             import relationship
from os import environ
import pandas as pd
from db import SessionLocal
from io import StringIO
from aws import S3
from requests_html import HTMLSession
import json
import copy
from pytz import timezone
from sqlalchemy_paginator import Paginator

Base = declarative_base()

class QueueProcesses(Base):
    __tablename__    = "tb_file_collection_process"
    process_id       = Column(Integer, primary_key=True, autoincrement=True)
    acquirer         = Column(String(20), default="ADYEN")
    obj_app          = Column(String(20), default="DOWNLOAD_ADYEN")
    user_app         = Column(String(20), default="PYTHON")
    start_date       = Column(DateTime)
    end_date         = Column(DateTime)
    queue_detail     = relationship("QueueDetail", cascade = "all, delete, delete-orphan", lazy="joined")

class QueueDetail(Base):
    __tablename__    = "tb_file_collection_process_detail"
    detailId = Column('detail_id', Integer, primary_key=True,  autoincrement=True)
    clientCode = Column('client_code', String(20))
    shortName = Column('short_name', String(100))
    storeCode = Column('store_code', String(100))
    merchantCode = Column('merchant_code', String(100))
    text = Column('text', String(255))
    error = Column('error', String(255))
    statusCode = Column('status_code', String(4))
    fileDate = Column('file_date', String(8))
    createdAt = Column('created_at', DateTime)
    endAt = Column('end_at', DateTime)
    isDone = Column('is_done', Boolean)
    isRunning = Column('is_running', Boolean, default=False)
    retrys = Column('retrys', Integer, default=0)
    processId = Column('process_id', Integer, ForeignKey('tb_file_collection_process.process_id'))
    webhookId = Column('webhook_id', Integer, ForeignKey('tb_file_collection_webhooks.webhook_id'), nullable=False)
    queue_process   = relationship("QueueProcesses")
    webhook   = relationship("WebHooks")

class WebHooks(Base):
    __tablename__= "tb_file_collection_webhooks"
    webhook_id      = Column(Integer, primary_key=True, autoincrement=True)
    text            = Column(String(2000))
    is_valid        = Column(Boolean, default=True)
    acquirer        = Column(String(30))

class Adyen:

    def __init__(self):
        pass
    
    def get_date(self, string: str, pos: int):
        return string[string.rindex('.')-pos: string.rindex('.')].replace('_', '')

    def get_adyen_links(self, url: str, user: str, password: str):
        asession = HTMLSession()
        return asession.get(url, auth=(user, password))     
    
    def reprocess(self, files) -> Dict:
        # IT'S FIND MERCHANT CREDENTIALS
        try:
            # SIMULATE NOTIFICATIONS BODY
            structure  = {
                "live": True,
                "notificationItems":[
                    {
                        "NotificationRequestItem": {
                            "amount": {
                            "currency":"EUR",
                            "value": 0
                            },
                            "eventCode":"REPORT_AVAILABLE",
                            "eventDate":"2020-11-11T06:14:02+01:00",
                            "merchantAccountCode":"GrandvisionBR_TEF_100211",
                            "merchantReference":"",
                            "pspReference":"payments_accounting_report_2020_11_10.csv",
                            "reason":"https://ca-live.adyen.com/reports/download/MerchantAccount/{merchant_code}/{filename}",
                            "success": True
                        }
                    }
                ]
            }
            eventDate = datetime.now().astimezone(timezone('America/Sao_Paulo'))
            notifications = []
            queue = QueueProcesses()
            for filename in files.files:
                structure["notificationItems"][0]["NotificationRequestItem"]["merchantAccountCode"] = files.merchantCode
                structure["notificationItems"][0]["NotificationRequestItem"]["eventDate"] = eventDate.isoformat()
                structure["notificationItems"][0]["NotificationRequestItem"]["pspReference"] = filename
                structure["notificationItems"][0]["NotificationRequestItem"]["reason"] = structure["notificationItems"][0]["NotificationRequestItem"]["reason"].format(merchant_code=files.merchantCode, filename=filename)
                
                request_file = QueueDetail(
                    clientCode=files.clientCode,
                    shortName=files.shortName,
                    storeCode=files.storeCode,
                    merchantCode=files.merchantCode,
                    text="Reprocessamento de arquivo",
                    error=structure["notificationItems"][0]["NotificationRequestItem"]["reason"],
                    createdAt=eventDate,
                    endAt=eventDate,
                    statusCode="REPC",
                    fileDate=eventDate.isoformat()[:10].replace('-', ''),
                    isDone=False,
                    isRunning=False,
                    retrys=0,
                    webhook=WebHooks(text=json.dumps(copy.deepcopy(structure), indent=4), acquirer="ADYEN")
                )
                queue.queue_detail.append(request_file)
        except Exception as error:
            print(str(error))
        finally:
            return queue

    def get_available_files(self, start_date: datetime, end_date: datetime, merchant_code: str, df_merchants: pd.DataFrame) -> Dict:
        # IT'S FIND MERCHANT CREDENTIALS
        username = df_merchants.iloc[0]['USERNAME']
        password = df_merchants.iloc[0]['PASSWORD']
        url = df_merchants.iloc[0]['URL']
        received_payments = []
        payments_accounting = []
        settlement_detail = []
        advancements_report = []
        try:
            if merchant_code and username and password:
                start_date = start_date.strftime("%Y%m%d")
                end_date = end_date.strftime("%Y%m%d")
                response = self.get_adyen_links(url, username, password)
                # GRAB AVAILABES LINKS FILES FROM ADYEN SITE
                # GET ONLY INTERESTING FILES
                received_payments = list(filter(lambda x: x.find('received_payments') >= 0 and start_date <= self.get_date(x, 10) <= end_date, response.html.links))
                settlement_detail = list(filter(lambda x: x.find('settlement_detail') >= 0 and start_date <= self.get_date(x, 8) <= end_date, response.html.links))
                payments_accounting = list(filter(lambda x: x.find('payments_accounting') >= 0 and start_date <= self.get_date(x, 10) <= end_date, response.html.links))
                advancements_report = list(filter(lambda x: x.find('advancements_report') >= 0 and start_date <= self.get_date(x, 10) <= end_date, response.html.links))
                # ORDER VALUES BY DATE
                received_payments.sort()
                payments_accounting.sort()
                advancements_report.sort()
                settlement_detail.sort(key=lambda x: int(x.split('_')[4]))
        except Exception as error:
            print(str(error))
        finally:
            received_payments.extend(payments_accounting)
            received_payments.extend(settlement_detail)
            received_payments.extend(advancements_report)
            df = pd.DataFrame(received_payments, columns=['fileName'])
            df['detailId'] = df['fileName']
            df['shortName'] = df_merchants.iloc[0]['EMPRESA']
            df['clientCode'] = df_merchants.iloc[0]['clientCode']
            df['storeCode'] = df_merchants.iloc[0]['FILIAL_CODIGO']
            df['merchantCode'] = merchant_code
            df['username'] = username
            df['password'] = password
            df['url'] = url            
            return df

class Stone:
    
    def __init__(self):
        pass

    def get_available_files(self, start_date: datetime, end_date: datetime, merchant_code: str, df_merchants: pd.DataFrame) -> pd.DataFrame:
        interval = pd.date_range(start_date,
                                end_date, 
                                freq='D', 
                                tz='America/Sao_Paulo')
        df = pd.DataFrame(interval, columns=['detailId'])
        df['detailId'] = df['detailId'].map(lambda x:  f"{x.strftime('%Y%m%d')}-STN-VP-D-v2.2-CFR-{df_merchants.iloc[0]['clientCode']}-{merchant_code}.text-plain.xml")
        df['fileName'] = df['detailId']
        df['shortName'] = df_merchants.iloc[0]['EMPRESA']
        df['clientCode'] = df_merchants.iloc[0]['clientCode']
        df['storeCode'] = df_merchants.iloc[0]['FILIAL_CODIGO']
        df['merchantCode'] = merchant_code
        df['username'] = "N/A"
        df['password'] = "N/A"
        df['url'] = interval.map(lambda x: f"https://conciliation.stone.com.br/v1/merchant/{merchant_code.strip()}/conciliation-file/{x.strftime('%Y%m%d')}") 
        return df        
        

class Acquirer:

    def __init__(self, acquirer: str):
        self.acquirer = acquirer
        self.session = SessionLocal()
        self.merchants = []

    def get_pendent_webhooks(self, acquirer: str) -> List["WebHooks"]:
        webhooks = []
        try:
            webhooks = self.session.query(WebHooks)\
                            .join(QueueDetail, isouter=True)\
                            .filter(QueueDetail.webhook_id==None)\
                            .filter(WebHooks.is_valid, WebHooks.acquirer==acquirer)\
                            .all()
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return webhooks

    def get_failed_download(self, acquirer: str):
        queue_files = []
        try:
            queue_files = self.session.query(QueueDetail)\
                            .join(WebHooks)\
                            .filter(WebHooks.is_valid, 
                                    WebHooks.acquirer==acquirer,
                                    QueueDetail.is_done==False,
                                    QueueDetail.error.notin_(['0', '200']),
                                    QueueDetail.retrys <= environ.get('RETRYS', 10),
                                    QueueDetail.error.like('%https://ca-live.adyen.com/reports/download/MerchantAccount%'))\
                            .all()
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return queue_files 

    def get_reports_download(self, start_date: datetime, end_date: datetime):
        df = []
        mapped_response = {}
        # {
        #     "data": [
        #         {
        #             "STONE": [{
        #                 "day": "01", 
        #                 "MerchantNotFound": 0, 
        #                 "Success": 0, 
        #                 "InternalServeErrors": 0
        #             }]
        #         }
        #     ],
        #     "mapKeys": ["MerchantNotFound", "Success", "InternalServeErrors"]
        # }
        try:
            queue_files = self.session.query(func.to_char(QueueDetail.createdAt, 'YYYY-MM-DD').label("day"), 
                                             func.count(QueueDetail.detailId).label("quantity"),
                                             QueueDetail.statusCode,
                                             QueueProcesses.acquirer)\
                                      .join(QueueProcesses, QueueDetail.processId==QueueProcesses.process_id)\
                                      .group_by("day", QueueDetail.statusCode, QueueProcesses.acquirer)\
                                      .filter(between(QueueDetail.createdAt, start_date, end_date))
            df = pd.read_sql(queue_files.statement, self.session.bind)
            # pivot table
            df['quantity'] = df['quantity'].astype(int)
            # print(df)
            df_pivot = df.pivot_table(values=['quantity'], index=df.index, columns=['status_code']).fillna('0').astype(int)
            df = df.merge(df_pivot, left_index=True, right_index=True, how='outer').sort_values('day')
            df = df.groupby(by=['acquirer', 'day']).sum().reset_index().drop(['quantity'], axis=1)
            responses = {
                '200': "BAIXADOS",
                '201': "BAIXADOS",
                '400': "BADREQUEST",
                '500': "ERRO INTERNO DA ADQUIRENTE",
                '401': "SEM CONCESSÃO",
                '403': "NÃO AUTORIZADO",
                '503': "TIMEOUT",
                '0': 'SEM CAD CONCIL',
                'REPC': 'AGUAR.REPROCESSAMENTO',
                'CANC': 'CANCELADO',
            }
            df.rename(columns={(name, status): responses[status] if status in responses else name for name, status  in df.columns[2:]}, inplace=True)     
            acquirers = df['acquirer'].unique().tolist()
            mapped_response = {
                acquirer: df.loc[df['acquirer']==acquirer].to_dict(orient='records') for acquirer in acquirers
            }
            mapkeys = {}
            for acquirer in acquirers:
                mapkeys[acquirer] = []
                for data in mapped_response[acquirer]:
                    mapkeys[acquirer].extend([key for key, value in data.items() if value and key not in ('day', 'acquirer')])
                    mapkeys[acquirer] = list(set(mapkeys[acquirer]))
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return mapped_response, mapkeys  
    
    def make_search_query(self, filters: list, query):
        for params in filters:
            if len(params['value']) and params['name'] == 'acquirer':
                query = query.filter(getattr(QueueProcesses, params['name']).ilike(f"%{params['value']}%"))
            elif len(params['value']):  # only fill values
                query = query.filter(getattr(QueueDetail, params['name']).ilike(f"%{params['value']}%"))
        return query

    def get_reports_download_detail(self, start_date: datetime, end_date: datetime, acquirer: str, filters: list, page:int, pageSize: int):
        df = []
        keys = []
        meta= {
            "total": 0,
            "current": page,
            "pageSize": pageSize
        }
        try:
                
            queue_files = self.session.query(QueueDetail, QueueProcesses.acquirer.label("acquirer"))\
                                      .select_from(QueueDetail)\
                                      .join(QueueProcesses, QueueDetail.processId==QueueProcesses.process_id)\
                                      .filter(
                                          between(QueueDetail.createdAt, start_date, end_date)
                                        )
            if acquirer != 'ALL':
                queue_files= queue_files.filter(QueueProcesses.acquirer==acquirer)
            
            if filters:
                queue_files = self.make_search_query(filters, queue_files)
            paginator = Paginator(queue_files, meta["pageSize"])
            page = paginator.page(meta["current"])
            meta["total"] = page.paginator.count
            meta["countPages"] = page.paginator.total_pages
            meta["previous_page_number"] = page.previous_page_number
            meta["next_page_number"] = page.next_page_number
            # queue_files = queue_files.limit(50)
            # print(meta)
            # print(page.object_list)

            # df = pd.read_sql(queue_files.statement, self.session.bind)
            objects = [    
                {
                    "detailId": item.detailId,
                    "clientCode": item.clientCode,
                    "shortName": item.shortName,
                    "storeCode": item.storeCode,
                    "merchantCode": item.merchantCode,
                    "text": item.text,
                    "error": item.error,
                    "statusCode": item.statusCode,
                    "fileDate": item.fileDate,
                    "createdAt": item.createdAt.isoformat() if item.createdAt else item.createdAt,
                    "endAt": item.endAt.isoformat() if item.endAt else item.endAt,
                    "isDone": item.isDone,
                    "isRunning": item.isRunning,
                    "retrys": item.retrys,
                    "webhookId": item.webhookId,
                    "acquirer": acquirer
                } for item, acquirer in page.object_list
            ]
            # print(objects)
            if not objects: return
            df = pd.DataFrame(objects)
            # df.rename(columns={name: "".join([name.split('_')[0], name.split('_')[1].capitalize()]) if len(name.split('_'))>1 else name for name in df.columns}, inplace=True)
            # print(len(df))
            df['webhookId'] = df['webhookId'].fillna(0).astype(int)
            keys = df.columns.tolist()
            df = df.to_dict(orient='records')
            # print(df)
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return df, keys, meta

    def describ_request(self, detail: QueueDetail):
        print(f"{detail.text} -> Client_code: {detail.client_code}, Merchant: {detail.merchant_code}, File Date: {detail.file_date}, retrys: {detail.retrys}, status_code: {detail.status_code} webhooK_id {detail.webhook_id}")

    def reprocess_files(self, files: list, status: str) -> None:
        try:
            queue_files = self.session.query(QueueDetail).filter(QueueDetail.detailId.in_(files)).\
                                       update({QueueDetail.statusCode: status}, synchronize_session=False)
            self.session.commit()
            files = self.session.query(QueueDetail).filter(QueueDetail.detailId.in_(files)).all()
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return files, []

    def get_acquirers_count(self, start_date: datetime, end_date: datetime):
        df = []
        # const data = [
        # { name: 'Adyen 25%', value: 25 },
        # { name: 'Group B', value: 25 },
        # { name: 'Group C', value: 25 },
        # { name: 'Group D', value: 25 },
        # ];
        try:
            queue_files = self.session.query(func.count(QueueDetail.detailId).label("quantity"),
                                             QueueProcesses.acquirer)\
                                      .join(QueueProcesses, QueueDetail.processId==QueueProcesses.process_id)\
                                      .group_by(QueueProcesses.acquirer)\
                                      .filter(between(QueueDetail.createdAt, start_date, end_date),
                                              QueueDetail.statusCode == '200')
            df = pd.read_sql(queue_files.statement, self.session.bind)
            # pivot table
            df['quantity'] = df['quantity'].fillna(0).astype(float)
            total = df['quantity'].sum()
            df['name'] = [f"{acquirer} {int((quantity/total*100))}%" for quantity, acquirer in df.itertuples(index=False)]
            df = df.drop('acquirer', axis=1).to_dict(orient="records")
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return df, []     
        
    def get_prevision_vs_current(self, start_date: datetime, end_date: datetime):
        df = []
        try:
            interval = (end_date - start_date)
            queue_files = self.session.query(func.count(QueueDetail.detailId).label("baixado"),
                                             QueueProcesses.acquirer.label("name"))\
                                      .join(QueueProcesses, QueueDetail.processId==QueueProcesses.process_id)\
                                      .group_by(QueueProcesses.acquirer, func.to_char(QueueDetail.createdAt, 'YYYY-MM-DD'))\
                                      .filter(between(QueueDetail.createdAt, start_date, end_date))\
                                      .filter(QueueDetail.statusCode == '200')
            df = pd.read_sql(queue_files.statement, self.session.bind)
            for acquirer in ["AME", "STONE", "PAYPAL", "ADYEN"]:
                df = df.append({"name": acquirer, "baixado": 0}, ignore_index=True)
            df = df.groupby('name').sum().reset_index()
            df['prev'] = [self.get_average((interval.days+1) or 1, acquirer) for acquirer, baixado in df.itertuples(index=False)]
            # print(df)
            # df['baixado'] = df['baixado'] *1000
        except Exception as error:
            print(str(error))
        finally:
            self.session.close()
            return df.to_dict(orient="records"), []

    def get_average(self, interval: int, acquirer: str):
        # nested querys
        sums = self.session.query(func.count(func.distinct(QueueDetail.detailId)).label("baixado"))\
                                      .join(QueueProcesses, QueueDetail.processId==QueueProcesses.process_id)\
                                      .group_by(func.to_char(QueueDetail.createdAt, 'YYYY-MM-DD'))\
                                      .filter(QueueDetail.statusCode == '200', QueueProcesses.acquirer==acquirer)\
                                      .subquery()
        average = self.session.query(func.avg(sums.c.baixado)).scalar() or 0
        return int(average * interval)

    def load_merchants(self, acquirer: str) -> list:
        df = []
        try:
            region = 'us-east-1'
            keys ={
                "AME": {
                    "region": "sa-east-1"
                }
            }
            if acquirer in keys:
                region = keys[acquirer]["region"]
            
            s3 = S3(p_bucket=f"concil-{environ.get('STAGE', 'dev')}-blackbox-{acquirer.lower()}", region_name=region)
            merchants = s3.get_object(p_key=f"establishment/CFR_ESTABELECIMENTOS_{acquirer.upper()}.csv")
            df = pd.read_csv(StringIO(merchants), sep=";")
            df = df.query("FILIAL_CODIGO != 'FILIAL_GERAL'", engine="python")
            df['ESTABELECIMENTO'] = df['ESTABELECIMENTO'].map(str)
            self.merchants = df
            # self.merchants.to_csv('test_establishments.csv', sep=',')
            df.rename(columns={"ESTABELECIMENTO": "merchantCode", "PFJ_CODIGO": "clientCode"}, inplace=True)
        except Exception as error:
            print(str(error))
        finally:
            return df[["merchantCode", "clientCode"]].to_dict(orient="records"), []

    def get_available_files(self, acquirer: str, start_date: datetime, end_date: datetime, merchant_code: str):
        df = []
        acquirers = {
            "ADYEN": Adyen,
            "STONE": Stone
        }
        self.load_merchants(acquirer)
        # print(self.merchants)
        if acquirer in ["ADYEN"]:
            merchant = self.merchants.query(f"merchantCode=='{merchant_code}' and FILIAL_CODIGO != 'FILIAL_GERAL' and USERNAME.str.len() and PASSWORD.str.len()", engine="python")
        else:
            merchant = self.merchants.query(f"merchantCode=='{merchant_code}'", engine="python")
            # print(merchant)
        df = acquirers[acquirer]().get_available_files(
                                        start_date=start_date, 
                                        end_date=end_date,
                                        merchant_code=merchant_code, 
                                        df_merchants=merchant
                                        )
        # print(results)
        return df.to_dict(orient="records"), []

    def reprocess(self, acquirer: str, files):
        reprocess = []
        message = "Arquivos processados com sucesso process id {queu_id}"
        try:
            acquirers = {
                "ADYEN": Adyen
            }
            queue = acquirers[acquirer]().reprocess(files)
            self.session.add(queue)
            self.session.commit()
            message = message.format(queu_id=queue.process_id)
        except Exception as error:
            message = str(error)
        finally:
            self.session.close()
            return message, []
    
    """Get reports availables values columns based on query filters"""
    def get_names(self, column: str, start_date: datetime, end_date: datetime, filters: list) -> List:
        #  start_time = time()
        mapped_values = {
            "installment_amount": lambda x: float(x) if x else 0,
            "createdAt": lambda x: x.isoformat() if x else None,
            "endAt": lambda x: x.isoformat() if x else None
        }
        response = {
            "meta": {
                # "limit": data['limit'],
                # "offset": data['offset'],
                "column": column,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                # "has_next": False,
                "filters": filters,
                "column": column
            },
            "data": []
        }
        status = 200
        try:
            # Only for conciliation_id status PENDENTE/CONCILIADO
            queue_files = self.session.query(func.distinct(getattr(QueueDetail if column != 'acquirer' else QueueProcesses, column)))\
                                      .select_from(QueueDetail)\
                                      .join(QueueProcesses, QueueDetail.processId==QueueProcesses.process_id)\
                                      .filter(between(QueueDetail.createdAt, start_date, end_date))
            if filters:
                queue_files = self.make_search_query(filters, queue_files)
            
            queue_files = queue_files.all()
            results = [mapped_values[column](x[0]) if column in mapped_values else x[0] for x in queue_files]
            response["data"] =  [{"value": value} for value in results]
        except Exception as error:
            print(error)
            status = 500
        finally:
            self.session.close()
            return response["meta"], response["data"], status