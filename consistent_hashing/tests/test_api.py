from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_node_api():
    response = client.get("/api/get-node/my-test-key")
    assert response.status_code == 200
    assert isinstance(response.json(), str)

def test_add_remove_node_api():
    # Adding a node
    add_response = client.post("/api/nodes/new-test-node")
    assert add_response.status_code == 201
    assert "new-test-node" in add_response.json()["current_nodes"]

    # Removing the node
    remove_response = client.delete("/api/nodes/new-test-node")
    assert remove_response.status_code == 200
    assert "new-test-node" not in remove_response.json()["current_nodes"]
