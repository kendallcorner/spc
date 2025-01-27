# SPC daily checker

Checks the Storm Prediction Center daily outlook for the risk level for Tulsa and sends a text message.

## Requirements

- aws cli
- docker
- poetry

## Run

``` bash
cp example.env .env
# Add twilio credentials to .env

poetry install
poetry run python spc.py
```

## Push Dockerfile

``` bash
./push_image.sh
```
