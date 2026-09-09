import pytest

from src.models.tree import Tree


@pytest.mark.modelTree
class TestModelTree:
    """Tree model tests"""

    def test_tree_initialization_empty(self, create_tree):
        """tests if empty tree can be initialized properly"""

        tree = create_tree()

        assert len(tree.entries) == 0
        assert tree.header == "tree 0"
        assert tree.serialize() == b"tree 0\x00"

    def test_tree_add_entry(self, create_tree):
        """tests if add_entry is working correctly"""

        e_hash = "4b825dc642cb6eb9a0f9e542d69221572b399201"
        e_type = "blob"
        e_name = "conftest"

        tree = create_tree()
        tree.add_entry(
            entry_hash=e_hash,
            entry_type=e_type,
            entry_name=e_name,
        )

        assert len(tree.entries) == 1
        assert tree.entries[0]["name"] == e_name
        assert tree.entries[0]["type"] == e_type
        assert tree.entries[0]["hash"] == e_hash

    def test_tree_serialize_payload_with_multiple_entries(self, create_tree):
        """tests if serialization with multiple entries is working correctly"""

        h1 = "1111111111111111111111111111111111111111"
        t1 = "blob"
        n1 = "main.py"

        h2 = "2222222222222222222222222222222222222222"
        t2 = "tree"
        n2 = "models"

        sample_entries = [
            {
                "hash": h1,
                "type": t1,
                "name": n1,
            },
            {
                "hash": h2,
                "type": t2,
                "name": n2,
            },
        ]

        tree = create_tree(entries=sample_entries)
        payload = tree.serialize_payload().decode()

        # type -> hash -> name
        expected_rows = [
            f"{t1} {h1} {n1}",
            f"{t2} {h2} {n2}",
        ]

        assert payload == "\n".join(expected_rows)

    def test_tree_full_serialization_binary_structure(self, create_tree):
        """tests if serialization can encode full binary structures"""

        sample_entries = [{"hash": "abc12345", "type": "blob", "name": "test.py"}]

        tree = create_tree(entries=sample_entries)
        serialized = tree.serialize()
        payload = tree.serialize_payload()
        header_bytes = f"{tree.header}\x00".encode()

        assert serialized.startswith(header_bytes)
        assert serialized == header_bytes + payload

    def test_tree_serialization_determinism_regardless_of_entry_order(
        self, create_tree
    ):
        """tests if entries added in different order produce the exact same serialized payload"""

        entry_a = {
            "hash": "1111111111111111111111111111111111111111",
            "type": "blob",
            "name": "a_file.py",
        }
        entry_b = {
            "hash": "2222222222222222222222222222222222222222",
            "type": "blob",
            "name": "b_file.py",
        }

        tree1 = create_tree(entries=[entry_a, entry_b])
        tree2 = create_tree(entries=[entry_b, entry_a])

        assert tree1.serialize_payload() == tree2.serialize_payload()
        assert tree1.serialize() == tree2.serialize()
    
    def test_tree_deserialization(self, create_tree):
        """tests if deserialization commences correctly"""
        
        entry_a = {
            "hash": "1111111111111111111111111111111111111111",
            "type": "blob",
            "name": "a_file.py",
        }
        entry_b = {
            "hash": "2222222222222222222222222222222222222222",
            "type": "blob",
            "name": "b_file.py",
        }

        tree = create_tree(entries=[entry_a, entry_b]) 
        serialized_tree = tree.serialize()
        deserialized_tree = Tree.deserialize(serialized_tree)
        
        assert tree == deserialized_tree
