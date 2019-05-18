
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

# Install pyexiv
WORKDIR /
#RUN pip install scons
#RUN apt-get install git -y
#RUN git clone https://github.com/escaped/pyexiv2
#WORKDIR /pyexiv2
#RUN scons install

# Remove the apt-get update list
RUN rm -rf /var/lib/apt/lists/*
RUN apt-get remove cmake -y

RUN mkdir /images
RUN mkdir /derived_imgs

WORKDIR /code
