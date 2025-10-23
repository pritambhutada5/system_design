from fastapi import APIRouter, HTTPException
from typing import List
from app.services.hashing_service import hashing_service
from app.core.logger_config import setup_logger
from app.core.config import settings

logger = setup_logger('api_router', log_file=settings.LOG_FILE_API)

router = APIRouter()


@router.get("/get-node/{key}", response_model=str, tags=["Hashing"])
def get_node_for_key(key: str):
    """
    Given a key, returns the node it is mapped to in the consistent hashing ring.
    This is the primary endpoint for determining data placement.
    """
    if not key:
        logger.warning("API call to /get-node/ received an empty key.")
        raise HTTPException(status_code=400, detail="Key cannot be empty.")

    node = hashing_service.get_node(key)

    if node is None:
        logger.error(f"No available nodes in the hash ring for key: '{key}'")
        raise HTTPException(status_code=503, detail="The hash ring is empty; no nodes available.")

    logger.info(f"Request for key '{key}' was successfully routed to node '{node}'.")
    return node


@router.post("/nodes/{node_name}", status_code=201, tags=["Cluster Management"])
def add_new_node(node_name: str):
    """
    Dynamically adds a new node to the consistent hashing ring.
    This simulates scaling up the cluster.
    """
    if not node_name:
        logger.warning("API call to add a node received an empty node name.")
        raise HTTPException(status_code=400, detail="Node name cannot be empty.")

    if node_name in hashing_service.get_all_nodes():
        logger.warning(f"Attempted to add node '{node_name}' which already exists.")
        raise HTTPException(status_code=409, detail=f"Node '{node_name}' already exists in the ring.")

    hashing_service.add_node(node_name)
    logger.info(f"Node '{node_name}' was added to the ring via API request.")

    return {"message": f"Node '{node_name}' added successfully.", "current_nodes": hashing_service.get_all_nodes()}


@router.delete("/nodes/{node_name}", tags=["Cluster Management"])
def remove_existing_node(node_name: str):
    """
    Dynamically removes an existing node from the consistent hashing ring.
    This simulates a server failure or scaling down the cluster.
    """
    if node_name not in hashing_service.get_all_nodes():
        logger.warning(f"Attempted to remove non-existent node '{node_name}' via API.")
        raise HTTPException(status_code=404, detail=f"Node '{node_name}' not found in the ring.")

    hashing_service.remove_node(node_name)
    logger.info(f"Node '{node_name}' was removed from the ring via API request.")

    return {"message": f"Node '{node_name}' removed successfully.", "current_nodes": hashing_service.get_all_nodes()}


@router.get("/nodes", response_model=List[str], tags=["Cluster Management"])
def get_all_nodes():
    """
    Returns a list of all physical nodes currently in the consistent hashing ring.
    """
    logger.info("API request to list all current nodes in the ring.")
    return hashing_service.get_all_nodes()
