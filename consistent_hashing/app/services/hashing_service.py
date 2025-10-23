from typing import List
from app.hashing.consistent_hashing import ConsistentHashing
from app.core.config import settings

class HashingService:
    """
    A service to manage the consistent hashing ring as a singleton.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HashingService, cls).__new__(cls)
            cls._instance.hash_ring = ConsistentHashing(nodes=settings.INITIAL_NODES)
        return cls._instance

    def get_node(self, key: str) -> str:
        return self.hash_ring.get_node(key)

    def add_node(self, node: str):
        self.hash_ring.add_node(node)

    def remove_node(self, node: str):
        self.hash_ring.remove_node(node)

    def get_all_nodes(self) -> List[str]:
        return self.hash_ring.nodes

hashing_service = HashingService()
