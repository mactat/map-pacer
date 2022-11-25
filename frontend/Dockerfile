FROM python:3.11.0b5-alpine3.16

# Default value; will be overridden by build-args, if passed
ARG ENV=production

ENV ENV $ENV

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

EXPOSE 8888
ENTRYPOINT ["python", "/app/app.py"]