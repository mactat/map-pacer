FROM python:3.11.0b5-alpine3.16

# Default value; will be overridden by build-args, if passed
ARG ENV=production

ENV ENV $ENV

WORKDIR /app

# Deps for psycopg2
RUN apk add python3-dev \
            libpq-dev \
            postgresql-dev \
            musl-dev \
            gcc

ADD ./backend/requirements.txt .
RUN pip install -r requirements.txt

COPY ./libs/ /app/libs/
ADD ./backend .


EXPOSE 8888
ENTRYPOINT ["python3", "/app/app.py"]