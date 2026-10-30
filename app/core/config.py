import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Academic Integrity AI & Plagiarism Checker"
    API_V1_STR: str = "/api/v1"
    
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
    
    # Plagiarism settings
    PLAGIARISM_THRESHOLD: float = 0.5
    MINHASH_NUM_PERM: int = 128
    
    # AI Detection (Binoculars)
    OBSERVER_MODEL: str = os.getenv("OBSERVER_MODEL", "tiiuae/falcon-7b")
    PERFORMER_MODEL: str = os.getenv("PERFORMER_MODEL", "tiiuae/falcon-7b-instruct")
    BINOCULARS_THRESHOLD: float = 0.9015355

    class Config:
        case_sensitive = True

settings = Settings()

