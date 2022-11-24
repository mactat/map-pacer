FROM python:3.11.0b5-alpine3.16

# Default value; will be overridden by build-args, if passed
ARG flask_env=production

ENV FLASK_ENV $flask_env

WORKDIR /app

ADD ./backend/requirements.txt .
RUN pip install -r requirements.txt

COPY ./libs/ /app/libs/
ADD ./backend .


EXPOSE 8888
ENTRYPOINT ["python", "/app/app.py"]