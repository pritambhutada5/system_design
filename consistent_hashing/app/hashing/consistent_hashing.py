import hashlib
import bisect
from typing import List, Dict, Optional
from app.core.logger_config import setup_logger
from app.core.config import settings

logger = setup_logger(__name__, log_file=settings.LOG_FILE_HASHING)

class ConsistentHashing:
    """
    A class to implement a consistent hashing ring for distributed systems.
    ...
    """

    def __init__(self, nodes: Optional[List[str]] = None, replicas: int = 100):
        self.replicas = replicas
        self.ring: Dict[int, str] = {}
        self.sorted_keys: List[int] = []
        self.nodes: List[str] = []

        if nodes:
            for node in nodes:
                self.add_node(node)

    def _hash(self, key: str) -> int:
        """Generates an integer hash for a given key using MD5.
            MD5 algorithm produces 128-bit hash and converts this hash into larger integer
            which represents a point on hash ring
        """
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node: str):
        """Adds a physical node to the hash ring, including its replicas to ensure uniform distribution"""
        if node in self.nodes:
            logger.warning(f"Node '{node}' already exists in the ring.")
            return

        logger.info(f"Adding node '{node}' with {self.replicas} replicas to the ring.")
        self.nodes.append(node)
        for i in range(self.replicas):
            replica_key = f"{node}:{i}"
            hash_key = self._hash(replica_key)
            self.ring[hash_key] = node
            bisect.insort(self.sorted_keys, hash_key)
        logger.debug(f"Ring size is now {len(self.sorted_keys)} after adding '{node}'.")

    def remove_node(self, node: str):
        """Removes a physical node and all its replicas from the hash ring."""
        if node not in self.nodes:
            logger.warning(f"Attempted to remove node '{node}', which does not exist.")
            return

        logger.info(f"Removing node '{node}' from the ring.")
        self.nodes.remove(node)
        keys_to_remove = []
        for i in range(self.replicas):
            replica_key = f"{node}:{i}"
            hash_key = self._hash(replica_key)
            keys_to_remove.append(hash_key)
            if hash_key in self.ring:
                del self.ring[hash_key]
        self.sorted_keys = [k for k in self.sorted_keys if k not in keys_to_remove]
        logger.debug(f"Ring size is now {len(self.sorted_keys)} after removing '{node}'.")

    def get_node(self, key: str) -> Optional[str]:
        """Finds the node responsible for a given key in the hash ring."""
        if not self.ring:
            logger.error("The hash ring is empty. Cannot find a node for the key.")
            return None

        hash_key = self._hash(key)
        idx = bisect.bisect_right(self.sorted_keys, hash_key)
        if idx == len(self.sorted_keys):
            idx = 0
        responsible_node = self.ring[self.sorted_keys[idx]]
        logger.debug(f"Key '{key}' (hash: {hash_key}) is mapped to node '{responsible_node}'.")
        return responsible_node

