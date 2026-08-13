import json

import pytest

from llamaindex_demo.config import DATA_DIR
from llamaindex_demo.local_models import LocalHashEmbedding
from llamaindex_demo.rag import build_and_persist_index


def test_persistence_writes_manifest_and_rejects_other_embedding(tmp_path):
    storage_dir = tmp_path / "storage"
    build_and_persist_index(
        DATA_DIR, storage_dir, LocalHashEmbedding(), rebuild=True
    )
    manifest = json.loads(
        (storage_dir / "demo_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["embedding_model"] == "local-hash-demo-v1"

    with pytest.raises(RuntimeError, match="--rebuild"):
        build_and_persist_index(
            DATA_DIR,
            storage_dir,
            LocalHashEmbedding(model_name="another-embedding"),
        )

