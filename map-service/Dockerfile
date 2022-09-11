FROM alpine:3.16

ARG ENVIROMENT=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

WORKDIR /app

ADD requirements.txt .

RUN apk --no-cache --update-cache add  python3 py3-pip py3-arrow  py3-numpy
RUN pip install --no-cache-dir -r requirements.txt

ADD . .

ENTRYPOINT ["python3", "/app/app.py"]