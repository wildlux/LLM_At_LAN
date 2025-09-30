"""
SDR (System Discovery and Researching) engine
"""

import ollama
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.ollama import OllamaEmbeddings
from langchain_community.llms.ollama import Ollama
from langchain.chains import RetrievalQA

class SDREngine:
    """Handles SDR functionality"""

    def __init__(self, upload_folder="./uploads", available_models=None):
        self.upload_folder = upload_folder
        self.available_models = available_models or ["llama2", "gemma3"]

    def query(self, query_text, selected_model="llama2"):
        """Process a query using SDR"""
        if selected_model not in self.available_models:
            raise ValueError(f"Model '{selected_model}' not available")

        # Load documents from folder
        loader = DirectoryLoader(self.upload_folder)
        documents = loader.load()

        if not documents:
            # No documents, respond directly
            prompt = f"Query: {query_text}\n\nAnswer:"
        else:
            # Create retriever with FAISS
            embeddings = OllamaEmbeddings()
            vectorstore = FAISS.from_documents(documents, embeddings)
            retriever = vectorstore.as_retriever()

            # Get relevant documents
            relevant_docs = retriever.get_relevant_documents(query_text)
            context = "\n".join([doc.page_content for doc in relevant_docs])

            # Create prompt with context
            prompt = f"Context: {context}\n\nQuery: {query_text}\n\nAnswer:"

        # Generate response using Ollama
        try:
            response = ollama.generate(model=selected_model, prompt=prompt)
            return response['response']
        except Exception as e:
            return f"Error generating response: {str(e)}. Please ensure Ollama is running and the model is loaded."

    def get_available_models(self):
        """Return list of available models"""
        return self.available_models