FROM python:2.7.8

RUN mkdir -p /app
WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

#EXPOSE 3000

CMD [ "python", "main.py"]
