# BASE LOCK - Ambiente Iniziale per Flask/Django

Questo repository fornisce un ambiente di base per avviare rapidamente progetti con Flask o Django, permettendoti di perdere meno tempo nella configurazione iniziale e concentrarti sullo sviluppo.

## Contenuto

- **Avvia_localmente_sito.py**: Script launcher con interfaccia TUI (Textual) per gestire server Flask, controllare l'ambiente, pulire cache e altro.

## Come usare

1. Clona il repository:
   ```
   git clone https://github.com/wildlux/BASE_LOCK_server_Django_flask__local.git
   cd BASE_LOCK_server_Django_flask__local
   ```

2. Attiva l'ambiente virtuale (se necessario) e avvia il launcher:
   ```
   source rag_env/bin/activate  # o . rag_env/bin/activate
   python Avvia_localmente_sito.py
   ```

3. Usa l'interfaccia TUI per:
   - Avviare/fermare il server Flask
   - Controllare lo status
   - Pulire cache
   - Configurare Flask/Django
   - Aprire il browser

## Benefici

- **Configurazione rapida**: Tutto pronto per iniziare senza setup lungo.
- **Interfaccia intuitiva**: TUI semplice per gestire il server.
- **Flessibile**: Adatto per Flask o Django con modifiche minime.
- **Risparmio di tempo**: Evita la configurazione manuale iniziale.

## Requisiti

- Python 3.x
- Virtual environment (raccomandato)
- Dipendenze: textual, flask, ecc. (installate automaticamente se necessario)

Inizia a sviluppare senza perdere tempo!