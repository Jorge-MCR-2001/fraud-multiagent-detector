from typing import List, Optional

import numpy as np

from openai import OpenAI, AzureOpenAI

import settings.paths as settings

# Obtener configuracion para el pipeline
def _get_setting(name: str, default=None):
    return getattr(settings, name, default)

# Verificar la naturaleza del valor
def _as_int_or_none(value) -> Optional[int]:
    if value is None:
        return None

    if value == "":
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None

class EmbeddingClient:

    """
        Cliente centralizado para el modulo RAG
        - No toma decisiones
        - Transforma texto en vectorstore para recuperacion semantica
    """

    def __init__(self) -> None:


        self.provider = str( # Cargar el proveedor del Embedding
            _get_setting("EMBEDDING_PROVIDER", "openai") or "openai"
        ).lower()

        self.dimensions = _as_int_or_none(
            _get_setting("EMBEDDING_DIMENSIONS", 1536)
        )

        if self.provider == "azure_openai":

            self._validate_azure_config()

            self.client = AzureOpenAI(
                api_key=_get_setting("AZURE_OPENAI_API_KEY"),
                azure_endpoint=_get_setting("AZURE_OPENAI_ENDPOINT"),
                api_version=_get_setting(
                    "AZURE_OPENAI_API_VERSION",
                    "2024-02-15-preview"
                ),
            )

            # Insertar el nombre del modelo
            self.model = (
                _get_setting("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
                or _get_setting("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
            )

        # Configuración con OPENAI
        if self.provider == "openai":

            self._validate_openai_config()

            self.client = OpenAI(
                api_key=_get_setting("OPENAI_API_KEY")
            )

            self.model = _get_setting(
                "EMBEDDING_MODEL",
                "text-embedding-3-small"
            )

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

        if self.dimensions is not None: # Validar si se inserto dimension de los embeddings
            request_payload["dimensions"] = self.dimensions

        try:

            # Generar embedding en base a modelo OpenSource
            response = self.client.embeddings.create(**request_payload)

        except Exception: # Algunos deployments de Azure OpenAI pueden no aceptar dimensions.
            if (
                self.provider == "azure_openai"
                and "dimensions" in request_payload
            ):
                request_payload.pop("dimensions", None)
                response = self.client.embeddings.create(**request_payload)
            else:
                raise

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
    
    # Validar configuracion de OPENAI
    def _validate_openai_config(self) -> None:
        missing = []

        if not _get_setting("OPENAI_API_KEY"):
            missing.append("OPENAI_API_KEY")

        if not _get_setting("EMBEDDING_MODEL", "text-embedding-3-small"):
            missing.append("EMBEDDING_MODEL")

        if missing:
            raise ValueError(
                "Faltan variables para EMBEDDING_PROVIDER=openai: "
                + ", ".join(missing)
            )

    # Validar configuracion de AzureOpenAI
    def _validate_azure_config(self) -> None:
        missing = []

        if not _get_setting("AZURE_OPENAI_ENDPOINT"):
            missing.append("AZURE_OPENAI_ENDPOINT")

        if not _get_setting("AZURE_OPENAI_API_KEY"):
            missing.append("AZURE_OPENAI_API_KEY")

        if not _get_setting("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"):
            missing.append("AZURE_OPENAI_API_VERSION")

        embedding_deployment = (
            _get_setting("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
            or _get_setting("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        )

        if not embedding_deployment:
            missing.append(
                "AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME "
                "or AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
            )

        if missing:
            raise ValueError(
                "Faltan variables para EMBEDDING_PROVIDER=azure_openai: "
                + ", ".join(missing)
            )