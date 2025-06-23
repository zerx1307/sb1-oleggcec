import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database configurations
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "mosdac_ai"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Vector database
    CHROMA_PERSIST_DIRECTORY: str = "./data/chroma_db"
    
    # ML Model configurations
    INTENT_MODEL_PATH: str = "./models/intent_classifier"
    NER_MODEL_PATH: str = "./models/ner_model"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    LLM_MODEL: str = "microsoft/DialoGPT-medium"
    
    # Data paths
    DATA_DIR: str = "./data"
    SCRAPED_DATA_DIR: str = "./data/scraped"
    PROCESSED_DATA_DIR: str = "./data/processed"
    
    # API settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 4
    
    # MOSDAC specific
    MOSDAC_BASE_URL: str = "https://www.mosdac.gov.in"
    CRAWL_DELAY: float = 1.0
    MAX_CONCURRENT_REQUESTS: int = 16
    
    class Config:
        env_file = ".env"

settings = Settings()