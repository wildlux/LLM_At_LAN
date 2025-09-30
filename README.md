# Sistema RAG con ChatGPT Style

Questo progetto implementa un sistema RAG (Retrieval-Augmented Generation) utilizzando Flask, LangChain e Ollama, con un'interfaccia web in stile ChatGPT.

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

## Installazione

1. Clona il repository:
   ```bash
   git clone https://github.com/wildlux/LLM_At_LAN.git
   cd LLM_At_LAN
   ```

2. Crea e attiva l'ambiente virtuale:
   ```bash
   python3 -m venv rag_env
   source rag_env/bin/activate  # Su Windows: rag_env\Scripts\activate
   ```

3. Installa le dipendenze:
   ```bash
   pip install -r requirements.txt
   ```

4. Avvia Ollama:
   ```bash
   ollama serve
   ```

5. Avvia il server:
   ```bash
   python rag_system.py
   ```

6. Apri il browser su `http://localhost:5001`

## Utilizzo

- **Carica File**: Usa il pannello laterale per caricare documenti.
- **Seleziona Modello**: Scegli il modello LLM dal menu.
- **Cambia Lingua**: Usa i pulsanti 🇮🇹/🇺🇸 per cambiare lingua.
- **Fai Domande**: Scrivi nella barra di inserimento e invia.

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