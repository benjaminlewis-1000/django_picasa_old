
FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
RUN apt-get update
RUN apt-get install vim -y
RUN apt-get install cmake -y
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
# Remove the apt-get update list
RUN rm -rf /var/lib/apt/lists/*
RUN apt-get remove cmake -y
