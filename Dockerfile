#Dockerfile
# using alpine to reduce image size
FROM python:3.7-alpine 
MAINTAINER Spencer Axford "saxford@mun.ca"

# dependancies required for 'Python Imaging Library'
RUN apk --update add \
    build-base \
    jpeg-dev \
    zlib-dev

# using layer caching to skip installs if requirements have not changed
COPY requirements.txt /

# install python requirements
RUN pip3 install -r /requirements.txt

# directory setup
COPY app/ /app
WORKDIR /app

#run flask app
ENTRYPOINT ["python3"]
CMD ["satmap.py"]
