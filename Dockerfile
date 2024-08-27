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

# Pokreni Gunicorn server
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000"]