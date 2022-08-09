FROM python:3.11.0b5-alpine3.16

# Default value; will be overridden by build-args, if passed
ARG ENVIROMENT=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

ENTRYPOINT ["python", "/app/app.py"]