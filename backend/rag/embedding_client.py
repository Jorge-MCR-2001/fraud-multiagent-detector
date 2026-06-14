from typing import List, Optional

import numpy as np

from openai import OpenAI, AzureOpenAI

from settings.paths import (
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL,
    EMBEDDING_DIMENSIONS,
    OPENAI_API_KEY,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    validate_embedding_environment
)

class EmbeddingClient:

    """
        Cliente centralizado para el modulo RAG
        - No toma decisiones
        - Transforma texto en vectorstore para recuperacion semantica
    """

    def __init__(self) -> None:

        validate_embedding_environment()

        self.provider = EMBEDDING_PROVIDER # Cargar el proveedor del Embedding
        
        # Configuración con OPENAI
        if self.provider == "openai": 
            self.client = OpenAI(api_key=OPENAI_API_KEY)
            self.model = EMBEDDING_MODEL
        
        # Configuración con AZURE OPENAI
        elif self.provider == "azure_openai":
            self.client = AzureOpenAI(
                api_key=AZURE_OPENAI_API_KEY,
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_version=AZURE_OPENAI_API_KEY
            )

            # Insertar el nombre del modelo
            self.model = AZURE_OPENAI_EMBEDDING_DEPLOYMENT

        else:
            raise ValueError(
                f"El proveedor no fue configurado correctamente: {self.provider}"
            )
        
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        # Genera embeddigns normalizados para una lista de textos

        clean_texts = []

        # Limpiar cada texto recibido
        for text in texts:
            clean_text = self._clean_text(text)
            clean_texts.append(clean_text)

        request_payload = {
            "model": self.model,
            "input": clean_texts,
            "encoding_format": "float"
        }

        if EMBEDDING_DIMENSIONS is not None: # Validar si se inserto dimension de los embeddings
            request_payload["dimensions"] = EMBEDDING_DIMENSIONS

        response = self.client.embeddings.create(**request_payload)

        vectors = []

        # Inyectar cada vector en la lista de vectores
        for item in response.data:
            vector = item.embedding
            vectors.append(vector)
        
        embeddings = np.array(vectors, dtype=np.float32)

        return self._normalize_embeddings(embeddings)

    def embed_query(self, query:str) -> np.ndarray:
        
        # Genera embedding normalizado de la consulta

        embeddings = self.embed_texts([query])

        return embeddings[0]
    
    def _clean_text(self, text:str) -> str:
        return str(text or ""). replace("\n", " ").strip()
    
    def _normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:

        # Normalizar los embeddings para la similud por cosenos
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0

        return embeddings/norms