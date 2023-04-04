#!/bin/sh

# variables
aws_region="us-east-1"
aws_account_id="317606636595"
aws_ecr_name="auth-service"

# pre-build
echo "authenticating the docker cli to use the ECR registry..."
aws ecr get-login-password --region $aws_region | docker login --username AWS --password-stdin $aws_account_id.dkr.ecr.$aws_region.amazonaws.com

# build
echo "building image..."
docker build -f Dockerfile -t $aws_account_id.dkr.ecr.$aws_region.amazonaws.com/$aws_ecr_name:dev .

# post-build
echo "pushing image to AWS ECR..."
docker push $aws_account_id.dkr.ecr.$aws_region.amazonaws.com/$aws_ecr_name:dev

echo "done!"
