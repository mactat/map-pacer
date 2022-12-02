FROM alpine:3.17

ARG ENVIROMENT=production
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

WORKDIR /app

ADD ./cloud-agent/requirements.txt .

# Python 3.11 from edge
RUN apk add python3 --repository=https://dl-cdn.alpinelinux.org/alpine/edge/main
RUN apk add py3-pip py3-arrow py3-numpy --repository=https://dl-cdn.alpinelinux.org/alpine/edge/community

RUN pip install --no-cache-dir -r requirements.txt

COPY ./libs/ /app/libs/
ADD ./cloud-agent/ .

ENTRYPOINT ["python3", "/app/app.py"]