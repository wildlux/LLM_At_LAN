"""
Local LLM Engine using llama-cpp-python for GGUF models
"""

from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import DirectoryLoader
from langchain.chains import RetrievalQA
import os

class LocalLLMEngine:
    """Handles local LLM functionality with GGUF models"""

    def __init__(self, models_dir="./models", upload_folder="./uploads", embedding_model="all-MiniLM-L6-v2"):
        self.models_dir = models_dir
        self.upload_folder = upload_folder
        self.embedding_model_name = embedding_model
        self.llm = None
        self.embeddings = None
        self.available_models = self._get_available_models()

    def _get_available_models(self):
        """Get list of available GGUF models in models directory"""
        if not os.path.exists(self.models_dir):
            return []
        models = [f for f in os.listdir(self.models_dir) if f.endswith('.gguf')]
        return models

    def load_model(self, model_name):
        """Load a specific GGUF model"""
        if model_name not in self.available_models:
            raise ValueError(f"Model '{model_name}' not found in {self.models_dir}")

        model_path = os.path.join(self.models_dir, model_name)
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )
        self.embeddings = SentenceTransformer(self.embedding_model_name)
        return True

    def query(self, query_text, selected_model="gemma-2b.gguf"):
        """Process a query using local LLM"""
        if not self.llm or not self.embeddings:
            if not self.load_model(selected_model):
                return "Error: No model loaded"

        # Load documents from folder
        loader = DirectoryLoader(self.upload_folder)
        documents = loader.load()

        if not documents:
            # No documents, respond directly
            prompt = f"Query: {query_text}\n\nAnswer:"
        else:
            # Create retriever with FAISS using local embeddings
            from langchain_community.embeddings import HuggingFaceEmbeddings
            hf_embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
            vectorstore = FAISS.from_documents(documents, hf_embeddings)
            retriever = vectorstore.as_retriever()

            # Get relevant documents
            relevant_docs = retriever.get_relevant_documents(query_text)
            context = "\n".join([doc.page_content for doc in relevant_docs])

            # Create prompt with context
            prompt = f"Context: {context}\n\nQuery: {query_text}\n\nAnswer:"

        # Generate response using local LLM
        try:
            response = self.llm(prompt, max_tokens=512)
            return response['choices'][0]['text'].strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def get_available_models(self):
        """Return list of available models"""
        return self.available_models