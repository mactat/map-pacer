FROM python:3.11.0b5-alpine3.16

# Default value; will be overridden by build-args, if passed
ARG flask_debug=1

ENV FLASK_DEBUG $flask_env

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD . .

EXPOSE 8888
ENTRYPOINT ["python", "/app/app.py"]