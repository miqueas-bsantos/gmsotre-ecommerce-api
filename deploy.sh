echo "Deploying API GmStore to $STAGE"
echo "_______________________________"

set -e

echo "$DOCKERHUB_PASSWORD" | docker login -u $DOCKERHUB_USERNAME --password-stdin

aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker build -f GmStore.DockerFile -t gmstore-api-$ACCOUNT_ID-$REGION .
docker tag gmstore-api-$ACCOUNT_ID-$REGION:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/gmstore-api-$ACCOUNT_ID-$REGION:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/gmstore-api-$ACCOUNT_ID-$REGION:latest

echo "_______________________________"
echo "Deployment Batch GmStore to $STAGE has finished"