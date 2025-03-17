FROM python:3.9

RUN apt update && apt install -y python3-pip
RUN pip3 install cryptography requests
