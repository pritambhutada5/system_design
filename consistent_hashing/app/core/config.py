from typing import List

class Settings:
    """
    Application settings.
    """
    INITIAL_NODES: List[str] = ["cache-node-1", "cache-node-2", "cache-node-3"]
    LOG_FILE_API: str = "api.log"
    LOG_FILE_HASHING: str = "hashing.log"

settings = Settings()
