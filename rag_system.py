from flask import Flask, request, jsonify, render_template
import os
import argparse
import signal
import sys
import ollama

# Librerie per Ollama (modifica secondo le specifiche di Ollama)
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.ollama import OllamaEmbeddings  # Usa Ollama per embeddings
from langchain_community.llms.ollama import Ollama  # Usa Ollama come LLM
from langchain.chains import RetrievalQA

# Configurazione Flask
app = Flask(__name__)

# Path della cartella dei file
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Modelli disponibili basati su quelli installati in Ollama
AVAILABLE_MODELS = ["rag-gemma3", "gemma3", "llama2", "qwen2.5-coder", "Esperto_Python"]


@app.route("/")
def home():
    """Homepage per caricare file e inviare richieste."""
    return render_template("index.html")


@app.route("/models", methods=["GET"])
def get_models():
    """Endpoint per ottenere l'elenco dei modelli disponibili."""
    return jsonify({"models": AVAILABLE_MODELS})


@app.route("/upload", methods=["POST"])
def upload_files():
    """Endpoint per caricare file nella cartella."""
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '' or file.filename is None:
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    return jsonify({"message": f"File '{file.filename}' uploaded successfully!"}), 200


@app.route("/query", methods=["POST"])
def query():
    """Endpoint per inviare una query e ottenere una risposta."""
    data = request.json
    if data is None:
        return jsonify({"error": "Invalid JSON"}), 400
    query_text = data.get("query", "")
    selected_model = data.get("model", "llama")  # Modello di default

    if not query_text:
        return jsonify({"error": "Query text is required"}), 400

    if selected_model not in AVAILABLE_MODELS:
        return jsonify({"error": f"Model '{selected_model}' is not available"}), 400

    # Caricamento documenti dalla cartella
    loader = DirectoryLoader(UPLOAD_FOLDER)
    documents = loader.load()

    if not documents:
        # Se non ci sono documenti, rispondi direttamente senza contesto
        prompt = f"Query: {query_text}\n\nAnswer:"
    else:
        # Creazione del retriever con FAISS
        embeddings = OllamaEmbeddings()  # Usa Ollama per embeddings
        vectorstore = FAISS.from_documents(documents, embeddings)
        retriever = vectorstore.as_retriever()

        # Ottieni documenti rilevanti
        relevant_docs = retriever.get_relevant_documents(query_text)
        context = "\n".join([doc.page_content for doc in relevant_docs])

        # Crea il prompt con contesto
        prompt = f"Context: {context}\n\nQuery: {query_text}\n\nAnswer:"

    # Usa ollama direttamente
    response = ollama.generate(model=selected_model, prompt=prompt)
    return jsonify({"response": response['response']}), 200


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the RAG system server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5001, help="Port to bind to (default: 5001)")
    args = parser.parse_args()
    
    def signal_handler(sig, frame):
        print('\nShutting down server...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Flask accessibile localmente
    print("Press Ctrl+C to stop the server.")
    app.run(host=args.host, port=args.port, debug=True)