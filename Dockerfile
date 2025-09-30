# Usa Python 3.13 slim come base
FROM python:3.13-slim

# Imposta la directory di lavoro
WORKDIR /app

# Installa dipendenze di sistema necessarie
RUN apt-get update && apt-get install -y \
    build-essential \
    libmagic1 \
    libmagic-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia il codice dell'applicazione
COPY . .

# Crea directory per uploads
RUN mkdir -p uploads

# Espone la porta
EXPOSE 5001

# Comando per avviare l'applicazione
CMD ["python", "rag_system.py"]