from app.hashing.consistent_hashing import ConsistentHashing


def test_add_and_get_node():
    ch = ConsistentHashing(nodes=['node1'])
    assert ch.get_node('some_key') == 'node1'


def test_distribution_change_on_add():
    ch = ConsistentHashing(nodes=['node1'])
    keys_to_test = [f"key-{i}" for i in range(100)]

    initial_mapping = {key: ch.get_node(key) for key in keys_to_test}
    assert all(node == 'node1' for node in initial_mapping.values())

    ch.add_node('node2')

    new_mapping = {key: ch.get_node(key) for key in keys_to_test}

    moved_keys = 0
    keys_on_node2 = 0
    for key in keys_to_test:
        if initial_mapping[key] != new_mapping[key]:
            assert new_mapping[key] == 'node2'
            moved_keys += 1
        if new_mapping[key] == 'node2':
            keys_on_node2 += 1

    assert keys_on_node2 > 0
    assert moved_keys == keys_on_node2
    assert moved_keys < len(keys_to_test)