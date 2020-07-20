FROM python:3.6

COPY requirements.txt .
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple

COPY . /code
WORKDIR /code
