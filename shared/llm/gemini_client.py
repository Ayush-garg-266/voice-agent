import os
import time
from typing import Optional, Any, List, Union
from google import genai
from google.genai import types
from google.genai.errors import APIError

from shared.config import settings
from shared.logging import logger

class GeminiClient:
    """
    Central production-ready Gemini Client wrapper powering Q1, Q2, Q3, and Q4.
    Strictly uses official google-genai SDK. Zero OpenAI dependencies.
    """

    def __init__(self, api_key: Optional[str] = None, default_model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")
        self.default_model = default_model or settings.GEMINI_MODEL or "gemini-1.5-flash"

        if not self.api_key or not self.api_key.strip():
            logger.error("GEMINI_API_KEY is missing!")
            raise ValueError(
                "GEMINI_API_KEY is not set. Please set GEMINI_API_KEY in your .env file or environment variables.\n"
                "Example: GEMINI_API_KEY=<your_gemini_api_key>"
            )

        try:
            self.client = genai.Client(api_key=self.api_key)
            self._embed_cache: dict[str, list[float]] = {}
            self.last_embedding_stats: dict[str, Any] = {
                "total_chunks": 0,
                "gemini_chunks": 0,
                "fallback_chunks": 0,
                "gemini_available": True
            }
            logger.info(f"GeminiClient initialized successfully using default model: {self.default_model}")
        except Exception as e:
            logger.error(f"Failed to initialize google-genai Client: {str(e)}")
            raise RuntimeError(f"Gemini client initialization failed: {str(e)}")

    def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = 0.7,
        max_output_tokens: Optional[int] = None,
        response_mime_type: Optional[str] = None,
        max_retries: int = 2
    ) -> str:
        """
        Generates text using the Gemini API with automatic model fallback and rate limit retries.
        """
        primary_model = model or self.default_model
        fallback_models = ["gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-2.5-flash"]
        models_to_try = [primary_model] + [m for m in fallback_models if m != primary_model]

        config_kwargs = {}
        if system_instruction:
            config_kwargs["system_instruction"] = system_instruction
        if temperature is not None:
            config_kwargs["temperature"] = temperature
        if max_output_tokens:
            config_kwargs["max_output_tokens"] = max_output_tokens
        if response_mime_type:
            config_kwargs["response_mime_type"] = response_mime_type

        config = types.GenerateContentConfig(**config_kwargs) if config_kwargs else None

        last_error = None
        for target_model in models_to_try:
            for attempt in range(max_retries + 1):
                start_time = time.time()
                try:
                    response = self.client.models.generate_content(
                        model=target_model,
                        contents=prompt,
                        config=config,
                    )
                    elapsed_ms = (time.time() - start_time) * 1000
                    logger.debug(f"Gemini generation completed in {elapsed_ms:.2f}ms (model: {target_model})")

                    if hasattr(response, "text") and response.text:
                        return response.text
                    else:
                        logger.warning(f"Gemini returned empty or blocked content. Response object: {response}")
                        return ""

                except Exception as e:
                    err_msg = str(e)
                    last_error = e
                    if any(k in err_msg for k in ["429", "503", "quota", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "404", "NOT_FOUND"]):
                        wait_sec = attempt + 1
                        logger.warning(f"Gemini API issue on model '{target_model}' ({err_msg[:80]}). Trying next model/retry in {wait_sec}s...")
                        time.sleep(wait_sec)
                        break
                    logger.error(f"Unexpected error during Gemini API call ({target_model}): {err_msg}")
                    break

        raise RuntimeError(f"Gemini generation failed across all models. Last error: {last_error}")

    def _generate_fallback_vector(self, text_item: str) -> List[float]:
        import hashlib
        import numpy as np
        h = hashlib.sha256(text_item.encode("utf-8")).digest()
        seed = int.from_bytes(h[:4], "big")
        rng = np.random.RandomState(seed)
        vec = rng.randn(768)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()

    def embed(
        self,
        contents: Union[str, List[str]],
        model: str = "gemini-embedding-001",
        max_retries: int = 1
    ) -> List[List[float]]:
        """
        Generates vector embeddings using Gemini API (gemini-embedding-001) with retry handling and fast fallback.
        """
        if isinstance(contents, str):
            contents = [contents]

        missing_indices = [idx for idx, item in enumerate(contents) if item not in self._embed_cache]

        gemini_count = len(contents) - len(missing_indices)
        fallback_count = 0
        circuit_broken = False

        if missing_indices:
            missing_contents = [contents[idx] for idx in missing_indices]
            batch_size = 10

            for i in range(0, len(missing_contents), batch_size):
                batch = missing_contents[i:i + batch_size]

                if circuit_broken:
                    logger.warning(f"Gemini embedding API rate-limited; fast-switching batch of {len(batch)} item(s) to deterministic fallback embedding.")
                    for text_item in batch:
                        self._embed_cache[text_item] = self._generate_fallback_vector(text_item)
                        fallback_count += 1
                    continue

                batch_success = False
                for attempt in range(max_retries + 1):
                    start_time = time.time()
                    try:
                        res = self.client.models.embed_content(
                            model=model,
                            contents=batch,
                        )
                        elapsed_ms = (time.time() - start_time) * 1000
                        logger.debug(f"Gemini embedding batch completed for {len(batch)} item(s) in {elapsed_ms:.2f}ms")

                        fetched: List[List[float]] = []
                        if hasattr(res, "embeddings") and res.embeddings:
                            fetched = [e.values for e in res.embeddings]
                        elif hasattr(res, "embedding") and res.embedding:
                            fetched = [res.embedding.values]
                        else:
                            raise ValueError("No embeddings returned in response.")

                        for text_item, emb in zip(batch, fetched):
                            self._embed_cache[text_item] = emb
                            gemini_count += 1

                        batch_success = True
                        break
                    except Exception as e:
                        if any(k in str(e).lower() for k in ["429", "quota", "resource_exhausted"]):
                            if attempt < max_retries:
                                logger.warning(f"Gemini embedding rate limit hit. Retrying in 0.5s...")
                                time.sleep(0.5)
                                continue
                        logger.warning(f"Gemini embedding API rate limit encountered for batch of {len(batch)} items: {e}")
                        break

                if not batch_success:
                    circuit_broken = True
                    logger.warning(f"Switching batch of {len(batch)} item(s) to deterministic fallback embedding due to Gemini rate limit.")
                    for text_item in batch:
                        self._embed_cache[text_item] = self._generate_fallback_vector(text_item)
                        fallback_count += 1

        self.last_embedding_stats = {
            "total_chunks": len(contents),
            "gemini_chunks": gemini_count,
            "fallback_chunks": fallback_count,
            "gemini_available": (fallback_count == 0)
        }

        return [self._embed_cache[item] for item in contents]


_client_instance: Optional[GeminiClient] = None

def get_gemini_client(api_key: Optional[str] = None, default_model: Optional[str] = None) -> GeminiClient:
    global _client_instance
    if _client_instance is None or api_key is not None:
        _client_instance = GeminiClient(api_key=api_key, default_model=default_model)
    return _client_instance
