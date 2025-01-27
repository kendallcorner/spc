# !/bin/bash

set -ex

aws ecr get-login-password --region us-east-2 --profile kendall | docker login --username AWS --password-stdin 340531845404.dkr.ecr.us-east-2.amazonaws.com
docker build . -t spc --provenance=false
export tag=$(date +%s)
docker tag spc 340531845404.dkr.ecr.us-east-2.amazonaws.com/spc:$tag
docker tag spc 340531845404.dkr.ecr.us-east-2.amazonaws.com/spc:latest
docker push 340531845404.dkr.ecr.us-east-2.amazonaws.com/spc:$tag
docker push 340531845404.dkr.ecr.us-east-2.amazonaws.com/spc:latest
