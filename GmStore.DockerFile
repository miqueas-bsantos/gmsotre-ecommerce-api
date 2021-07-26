FROM ubuntu:18.04
MAINTAINER Miqueas Santos


COPY . /gmstore-api
WORKDIR /gmstore-api

RUN apt-get update -y
RUN apt-get install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get update -y
RUN apt-get install libpq-dev python-dev -y
RUN apt-get install python3-pip -y
RUN chmod 777 -R /gmstore-api/
# RUN pip3 install -r /gmstore-api/requirements.txt
RUN chmod 777 -R /gmstore-api/

# CMD python3 /gmstore-api/src/handler.py


# comando para biuld #
#docker build -f BlackBox.DockerFile -t miqueassantos/gmstore-api .

# deploy imagem aws
#docker tag miqueassantos/gmstore-api:latest 640194322443.dkr.ecr.us-east-1.amazonaws.com/concil-gmstore-api-640194322443-us-east-1:latest
#aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 640194322443.dkr.ecr.us-east-1.amazonaws.com
#aws ecr get-login --no-include-email --region us-east-1
#docker push 640194322443.dkr.ecr.us-east-1.amazonaws.com/concil-gmstore-api-640194322443-us-east-1