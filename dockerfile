FROM python:3

RUN mkdir /app
WORKDIR /app
COPY web.py .
COPY requirements.txt .
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "web.py"]

