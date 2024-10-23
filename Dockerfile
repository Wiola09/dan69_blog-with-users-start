# Koristi Python sličicu kao osnovnu sliku
FROM python:3.8-slim

# Postavi radni direktorijum u kontejneru
WORKDIR /usr/src/app

# Klone GitHub repozitorijum sa vašim kodom
RUN apt-get update && apt-get install -y git
RUN git clone https://github.com/Wiola09/dan69_blog-with-users-start.git .

COPY . /usr/src/app

# Instaliraj zavisnosti
RUN pip install -r requirements.txt

# Izloži port na kojem će aplikacija slušati
EXPOSE 8000

# Kreiraj direktorijum za logove
RUN mkdir -p /var/log/gunicorn

# Dodaj CMD komandu sa logovanjem
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "--access-logfile", "/var/log/gunicorn/access.log", "--error-logfile", "/var/log/gunicorn/error.log"]
