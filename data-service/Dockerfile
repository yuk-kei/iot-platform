FROM python:3.11
COPY requirements.txt /data-app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
COPY . /app
CMD ["gunicorn", "-c", "guni_config.py", "run:app"]
EXPOSE 9001