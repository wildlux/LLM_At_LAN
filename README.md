# Sistema Discovery and Researching con ChatGPT Style

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.1+-green.svg)](https://flask.palletsprojects.com/)
[![License: GPL-3.0](https://img.shields.io/badge/License-GPL--3.0-yellow.svg)](https://opensource.org/licenses/GPL-3.0)
[![Ollama](https://img.shields.io/badge/ollama-latest-orange.svg)](https://ollama.com/)

Questo progetto implementa un sistema Discovery and Researching utilizzando Flask, LangChain e Ollama, con un'interfaccia web moderna in stile ChatGPT.

## 🚀 Caratteristiche

- **Interfaccia Web Moderna**: Design scuro in stile ChatGPT con sidebar collassabile
- **Supporto Multilingue**: Italiano e Inglese con selezione della lingua
- **Caricamento File**: Drag & drop per documenti con supporto per vari formati
- **Modelli LLM**: Utilizza modelli Ollama come Gemma3, Llama2, ecc.
- **Temi**: Scelta tra tema scuro e chiaro
- **TUI Opzionale**: Interfaccia terminale per monitoring e controllo

## Caratteristiche

- **Interfaccia Web Moderna**: Design scuro in stile ChatGPT con sidebar collassabile.
- **Supporto Multilingue**: Italiano e Inglese con selezione della lingua.
- **Caricamento File**: Carica documenti per il retrieval.
- **Modelli LLM**: Utilizza modelli Ollama come Gemma3, Llama2, ecc.
- **Temi**: Scelta tra tema scuro e chiaro.
- **TUI Opzionale**: Interfaccia terminale per monitoring.

## Requisiti

- Python 3.13+
- Ollama installato e in esecuzione
- Modelli scaricati in Ollama (es. `ollama pull gemma3`)

## ⚡ Avvio Rapido (LAN Ready)

```bash
# 1. Clona il repository
git clone https://github.com/wildlux/LLM_At_LAN.git
cd LLM_At_LAN

# 2. Avvia Ollama (in un terminale separato)
ollama serve

# 3. Avvia il sistema Discovery and Researching
./start.sh

# 4. Il TUI si aprirà automaticamente
# 5. Usa il TUI per gestire il server web
# 6. Accedi da qualsiasi dispositivo sulla rete:
# http://IP_DEL_SERVER:5001 (es. http://192.168.1.100:5001)
```

**Tempo di setup stimato**: 2-3 minuti
**Accesso LAN**: L'app è configurata per essere accessibile da tutta la rete locale
**Gestione**: Usa il TUI per un controllo completo del sistema

## 📖 Utilizzo

### Interfaccia Web
- **Carica File**: Trascina file nel pannello laterale o clicca per selezionare
- **Seleziona Modello**: Scegli il modello LLM dal menu a tendina
- **Cambia Lingua**: Usa i pulsanti 🇮🇹/🇺🇸 per cambiare lingua
- **Fai Domande**: Scrivi nella barra di inserimento e invia
- **Sidebar**: Usa il pulsante ☰ per mostrare/nascondere il pannello laterale

### Interfaccia TUI (Terminale)
```bash
# Avvia il sistema (lancia automaticamente il TUI)
./start.sh

# Oppure manualmente:
python tui.py
```
- **Menu Interattivo**: Controlli per avviare/fermare il server
- **Monitoraggio**: Visualizza log e stato del sistema
- **Gestione Ollama**: Controlla modelli e servizi
- **Tasti Rapidi**: Usa 'q' per uscire, 'r' per aggiornare
- **Auto-lancio**: start.sh avvia automaticamente il TUI

## 🔧 Risoluzione Problemi

### Errore "Port 5001 già in uso"
```bash
# Trova e termina i processi che usano la porta
lsof -ti:5001 | xargs kill -9
# Oppure usa il TUI: python tui.py e premi "Check Port 5001"
```

### Ollama non trovato o non funziona
```bash
# Verifica che Ollama sia installato e in esecuzione
which ollama
ollama list
ollama serve  # Riavvia se necessario
```

### Modelli non disponibili
```bash
# Scarica modelli necessari
ollama pull gemma3
ollama pull llama2
```

### Dipendenze mancanti
```bash
# Installa dipendenze specifiche
pip install faiss-cpu flask langchain langchain-community ollama textual
```

### Memoria insufficiente per modelli
- Usa modelli più piccoli (es. `llama2:7b` invece di `llama2:70b`)
- Chiudi altre applicazioni per liberare RAM
- Considera l'uso di GPU se disponibile

### File upload non funziona
- Verifica che il file sia di un formato supportato
- Controlla i log del server per errori specifici
- Riavvia il server se necessario

## Struttura del Progetto

- `rag_system.py`: Server Flask principale.
- `templates/index.html`: Interfaccia web.
- `requirements.txt`: Dipendenze Python.
- `start.sh`: Script di avvio.
- `LLM/`: Modelli personalizzati e Modelfile.

## Contribuire

Le pull request sono benvenute. Per modifiche importanti, apri prima una issue.

## Licenza

GPL-3.0 License. Vedi LICENSE per dettagli.