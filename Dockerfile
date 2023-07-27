#FROM python:bullseye  
FROM jenkins/jenkins:lts-jdk11
WORKDIR /app

COPY ./app/ .
#COPY ./entrypoint.sh .

EXPOSE 5678
EXPOSE 8080
EXPOSE 5000

# install ffmpeg and dependencies
# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

# install neccesary packages for shuffle and validation
# RUN pip install opencv-python
# RUN pip install pytesseract
# RUN pip install ffmpeg
# RUN apt install tesseract-ocr -y

# RUN chmod a+x ./entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]