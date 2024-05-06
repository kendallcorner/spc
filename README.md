# SPC daily checker

Checks the Storm Prediction Center daily outlook for the risk level for Tulsa and sends a text message. 

## Run
```
cp example.env .env
# Add twilio credentials to .env

poetry install
poetry run python spc.py
```

## Push Dockerfile

```
./push_image.sh
```
