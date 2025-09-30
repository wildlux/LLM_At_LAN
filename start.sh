#!/bin/bash

# Controlla se l'ambiente virtuale esiste
if [ ! -d "rag_env" ]; then
    echo "Creazione dell'ambiente virtuale..."
    python3 -m venv rag_env
    echo "Installazione delle dipendenze..."
    . rag_env/bin/activate
    pip install -q -r requirements.txt
else
    echo "Attivazione dell'ambiente virtuale..."
    . rag_env/bin/activate
    echo "Installazione delle dipendenze..."
    pip install -q -r requirements.txt
fi

# Avvia l'applicazione Flask
echo "Avvio dell'applicazione Flask..."
rag_env/bin/python rag_system.py