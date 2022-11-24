FROM alpine:3.16
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=UTF-8

ARG ENVIROMENT=production

WORKDIR /app
RUN apk --no-cache --update-cache add  python3 py3-pip

ADD ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD ./test.py ./backend_api.py ./
ADD ./maps/ ./maps/

ENTRYPOINT ["tail", "-f", "/dev/null"]