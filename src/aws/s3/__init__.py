import boto3
from config import environ


class S3():
    def __init__(self, p_bucket: str, 
                 aws_access_key_id=environ['aws_access_key_id'],
                 aws_secret_access_key=environ['aws_secret_access_key'],
                 region_name="us-east-1"):
        self.p_bucket = p_bucket
        self.s3 = boto3.resource(
            's3', 
            region_name=region_name
        )

    def get_object(self, p_key):
        try:
            obj = self.s3.Object(self.p_bucket, p_key)
            data = obj.get()["Body"].read().decode("utf-8")
            return data
        except Exception as error:
            return str(error)

    def get_object_as_object(self, p_key):
        try:
            obj = self.s3.Object(self.p_bucket, p_key)
            data = obj.get()["Body"]
            return data
        except Exception as error:
            return str(error)

    def put_object(self, p_key, p_file):
        try:
            bucket = self.s3.Bucket(self.p_bucket)
            bucket.put_object(Bucket=self.p_bucket, Key=p_key, Body=p_file)
            return  'Success'
        except Exception as error:
            return str(error)

    def delete_object(self, p_key):
        try:
            obj = self.s3.Object(self.p_bucket, p_key)
            obj.delete()
            return 'Success'
        except Exception as error:
            return str(error)

    def exist_object(self, p_key):
        try:
            bucket = self.s3.Bucket(self.p_bucket)
            objs = list(bucket.objects.filter(Prefix=p_key))
            if len(objs) > 0 and objs[0].key == p_key:
                return True
            else:
                return False
        except Exception as error:
            return str(error)

    def list_all_objects(self):
        try:
            l_file_bk = list()
            bucket = self.s3.Bucket(self.p_bucket)
            for i in bucket.objects.all():
                l_file_bk.append(i.key)
            return l_file_bk
        except Exception as error:
            return str(error)

    def list_path_objects(self, p_path):
        try:
            l_file_bk = list()
            bucket = self.s3.Bucket(self.p_bucket)
            for obj in list(bucket.objects.filter(Prefix=p_path)):
                l_file_bk.append(obj.key)
            return l_file_bk
        except Exception as error:
            return str(error)

    def list_like_objects(self, p_like):
        try:
            l_file_bk = list()
            bucket = self.s3.Bucket(self.p_bucket)
            for i in bucket.objects.all():
                if p_like in i.key:
                    l_file_bk.append(i.key)
            return l_file_bk
        except Exception as error:
            return str(error)

    def copy_object_another_bucket(self, p_bucket_ori, p_key_ori, p_bucket_dest, p_key_dest):
        try:
            copy_source = {'Bucket': p_bucket_ori
                         , 'Key': p_key_ori}
            bucket = self.s3.Bucket(p_bucket_dest)
            bucket.copy(copy_source, p_key_dest)
            return 'Success'
        except Exception as error:
            return str(error)