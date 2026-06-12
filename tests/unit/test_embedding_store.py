from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from omnisense_embedding import InMemoryEmbeddingStore
from omnisense_osip import EmbeddingRef, PerceptPacket

FIXTURE_DIR = Path(__file__).parents[1] / "fixtures" / "osip"


def load_fixture(filename: str) -> dict[str, Any]:
    data = json.loads((FIXTURE_DIR / filename).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def embedding_ref(ref: str = "emb_audio_001") -> EmbeddingRef:
    return EmbeddingRef(ref=ref, dimension=3, space="audio_event_v1")


def test_in_memory_store_upserts_and_gets_embedding_record() -> None:
    store = InMemoryEmbeddingStore()
    ref = embedding_ref()

    record = store.upsert(
        ref,
        [0.1, 0.2, 0.3],
        source_message_id="perc_001",
        trace_id="trace_001",
        correlation_id="corr_001",
        metadata={"scenario_id": "room_smoke_replay"},
    )

    assert store.get(ref) == record
    assert store.get("emb_audio_001") == record
    assert record.vector == (0.1, 0.2, 0.3)
    assert record.metadata["scenario_id"] == "room_smoke_replay"
    assert store.stats().total_records == 1
    assert store.stats().spaces == {"audio_event_v1": 1}


def test_in_memory_store_upserts_percept_embedding_with_provenance() -> None:
    store = InMemoryEmbeddingStore()
    data = load_fixture("percept_packet.json")
    data["trace_id"] = "trace_audio_001"
    data["correlation_id"] = "corr_audio_001"
    percept = PerceptPacket.model_validate(data)

    record = store.upsert_percept(percept, [1.0] + [0.01] * 511, metadata={"split": "replay"})

    assert record.ref == percept.embedding
    assert record.source_message_id == "perc_000001"
    assert record.trace_id == "trace_audio_001"
    assert record.correlation_id == "corr_audio_001"
    assert record.metadata["message_type"] == "percept.packet"
    assert record.metadata["source_model"] == "audio.event_classifier_v1"
    assert record.metadata["modality"] == "audio"
    assert record.metadata["split"] == "replay"


def test_in_memory_store_requires_percept_embedding_reference() -> None:
    store = InMemoryEmbeddingStore()
    data = load_fixture("percept_packet.json")
    data["embedding"] = None
    percept = PerceptPacket.model_validate(data)

    with pytest.raises(ValueError, match="does not contain an embedding reference"):
        store.upsert_percept(percept, [0.1, 0.2, 0.3])


def test_in_memory_store_rejects_dimension_mismatch() -> None:
    store = InMemoryEmbeddingStore()

    with pytest.raises(ValueError, match="dimension 2 does not match expected 3"):
        store.upsert(embedding_ref(), [0.1, 0.2])


def test_in_memory_store_rejects_non_finite_or_zero_vectors() -> None:
    store = InMemoryEmbeddingStore()

    with pytest.raises(ValueError, match="finite"):
        store.upsert(embedding_ref("emb_bad_nan"), [0.1, float("nan"), 0.3])

    with pytest.raises(ValueError, match="norm"):
        store.upsert(embedding_ref("emb_bad_zero"), [0.0, 0.0, 0.0])


def test_in_memory_store_rejects_incompatible_ref_reuse() -> None:
    store = InMemoryEmbeddingStore()
    store.upsert(embedding_ref("emb_reused"), [1.0, 0.0, 0.0])

    with pytest.raises(ValueError, match="already exists"):
        store.upsert(
            EmbeddingRef(ref="emb_reused", dimension=2, space="audio_event_v2"),
            [1.0, 0.0],
        )


def test_in_memory_store_search_is_space_scoped_and_ranked() -> None:
    store = InMemoryEmbeddingStore()
    store.upsert(embedding_ref("emb_a"), [1.0, 0.0, 0.0])
    store.upsert(embedding_ref("emb_b"), [0.8, 0.2, 0.0])
    store.upsert(embedding_ref("emb_c"), [0.0, 1.0, 0.0])
    store.upsert(
        EmbeddingRef(ref="emb_other", dimension=3, space="thermal_event_v1"),
        [1.0, 0.0, 0.0],
    )

    hits = store.search([1.0, 0.0, 0.0], space="audio_event_v1", limit=2)

    assert [hit.record.ref.ref for hit in hits] == ["emb_a", "emb_b"]
    assert hits[0].score == pytest.approx(1.0)
    assert hits[1].score > 0.9


def test_in_memory_store_search_validates_query_and_filters_score() -> None:
    store = InMemoryEmbeddingStore()
    store.upsert(embedding_ref("emb_a"), [1.0, 0.0, 0.0])
    store.upsert(embedding_ref("emb_b"), [0.0, 1.0, 0.0])

    hits = store.search([1.0, 0.0, 0.0], space="audio_event_v1", min_score=0.5)

    assert [hit.record.ref.ref for hit in hits] == ["emb_a"]

    with pytest.raises(ValueError, match="limit"):
        store.search([1.0, 0.0, 0.0], space="audio_event_v1", limit=0)

    with pytest.raises(ValueError, match="min_score"):
        store.search([1.0, 0.0, 0.0], space="audio_event_v1", min_score=2.0)

    with pytest.raises(ValueError, match="dimension 2"):
        store.search([1.0, 0.0], space="audio_event_v1")


def test_in_memory_store_delete_reports_existing_and_missing_refs() -> None:
    store = InMemoryEmbeddingStore()
    store.upsert(embedding_ref(), [1.0, 0.0, 0.0])

    assert store.delete("emb_audio_001") is True
    assert store.get("emb_audio_001") is None
    assert store.delete("emb_audio_001") is False
