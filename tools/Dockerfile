FROM alpine:3.16

WORKDIR /app

ADD ./requirements.txt .

RUN apk --no-cache --update-cache add  python3 py3-pip py3-arrow  py3-numpy py3-pandas py3-matplotlib
RUN pip install --no-cache-dir -r requirements.txt
