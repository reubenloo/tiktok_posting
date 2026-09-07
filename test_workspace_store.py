"""Tests for durable workspace storage and the per-project status timeline.

These cover the two things the workspace could not previously do: survive a restart, and
show a real history for each project.
"""

import importlib
import os
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture()
def store(monkeypatch):
    """A store module bound to a throwaway database file."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "test-workspace.db"
    monkeypatch.setenv("EM_POSTING_DB_PATH", str(db_path))

    import store as store_module

    importlib.reload(store_module)
    store_module.init_db()
    yield store_module
    store_module.reset()


def _project(pid="proj-test", **overrides):
    base = {
        "id": pid,
        "title": "A test project",
        "filename": "test.mp4",
        "duration": "00:08",
        "size_mb": 0.11,
        "creator": "Creator (primary)",
        "status": "ready",
        "caption": "",
        "created": "2026-09-07 10:00 UTC",
        "reviewed": False,
        "approved": False,
        "checks": {"rights": False, "reviewed": False, "policy": False, "control": False, "consent": False},
        "is_sample": False,
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------- persistence


def test_db_path_honours_env_override(store):
    assert store.db_path().name == "test-workspace.db"


def test_projects_survive_a_reconnect(store):
    store.save_projects([_project("proj-a"), _project("proj-b")])
    # A fresh read opens a new connection, exactly like a browser refresh would.
    loaded = store.load_projects()
    assert [p["id"] for p in loaded] == ["proj-a", "proj-b"]


def test_project_order_is_preserved(store):
    store.save_projects([_project(f"proj-{i}") for i in range(5)])
    assert [p["id"] for p in store.load_projects()] == [f"proj-{i}" for i in range(5)]


def test_upsert_updates_in_place_without_duplicating(store):
    store.save_projects([_project("proj-a"), _project("proj-b")])
    updated = _project("proj-a", status="approved", approved=True)
    store.upsert_project(updated)

    loaded = store.load_projects()
    assert len(loaded) == 2
    by_id = {p["id"]: p for p in loaded}
    assert by_id["proj-a"]["status"] == "approved"
    assert by_id["proj-a"]["approved"] is True


def test_approval_state_persists(store):
    """The regression that mattered: an approval used to die on refresh."""
    store.save_projects([_project("proj-a")])
    approved = _project(
        "proj-a",
        status="approved",
        approved=True,
        checks={"rights": True, "reviewed": True, "policy": True, "control": True, "consent": True},
    )
    store.upsert_project(approved)

    reloaded = store.load_projects()[0]
    assert reloaded["status"] == "approved"
    assert all(reloaded["checks"].values())


def test_project_count(store):
    assert store.project_count() == 0
    store.save_projects([_project("proj-a"), _project("proj-b")])
    assert store.project_count() == 2


# ----------------------------------------------------------------------------- activity


def test_activity_round_trips_newest_first(store):
    store.append_activity({"type": "create", "text": "first", "time": "10:00"})
    store.append_activity({"type": "approve", "text": "second", "time": "10:05"})
    log = store.load_activity()
    assert [entry["text"] for entry in log] == ["second", "first"]


def test_activity_log_is_bounded(store):
    for i in range(250):
        store.append_activity({"type": "create", "text": f"entry-{i}", "time": "10:00"})
    assert len(store.load_activity(limit=500)) <= 200


# ------------------------------------------------------------------------------- events


def test_events_are_ordered_oldest_first(store):
    store.append_event("proj-a", "created", "10:00", "Uploaded test.mp4")
    store.append_event("proj-a", "approved", "10:05", "All five compliance checks confirmed")
    store.append_event("proj-a", "handed_off", "10:09", "TikTok status: SEND_TO_USER_INBOX")

    events = store.load_events("proj-a")
    assert [e["stage"] for e in events] == ["created", "approved", "handed_off"]


def test_event_payload_carries_publish_id(store):
    store.append_event(
        "proj-a",
        "handed_off",
        "10:09",
        "TikTok status: SEND_TO_USER_INBOX",
        {"publish_id": "v_pub_file~abc123", "status": "SEND_TO_USER_INBOX"},
    )
    event = store.load_events("proj-a")[0]
    assert event["data"]["publish_id"] == "v_pub_file~abc123"
    assert event["data"]["status"] == "SEND_TO_USER_INBOX"


def test_events_are_scoped_per_project(store):
    store.append_event("proj-a", "created", "10:00")
    store.append_event("proj-b", "created", "10:01")
    assert len(store.load_events("proj-a")) == 1
    assert len(store.load_events("proj-b")) == 1
    assert store.event_count() == 2


def test_events_survive_a_reconnect(store):
    store.append_event("proj-a", "created", "10:00", "Uploaded test.mp4")
    assert store.load_events("proj-a")[0]["detail"] == "Uploaded test.mp4"


# --------------------------------------------------------------------------- seed data


def test_seed_catalogue_is_non_trivial():
    import seed_data

    projects = seed_data.seed_projects()
    # The whole point of the seed is that the library no longer looks empty.
    assert len(projects) >= 20


def test_seed_projects_have_required_library_fields():
    import seed_data

    required = {"id", "title", "filename", "creator", "status", "created", "checks"}
    for project in seed_data.seed_projects():
        assert required <= set(project), f"missing fields on {project.get('id')}"


def test_seed_projects_are_marked_published_and_not_samples():
    import seed_data

    for project in seed_data.seed_projects():
        assert project["status"] == "published"
        assert project["is_sample"] is False
        assert project["is_seed"] is True


def test_seed_projects_have_unique_ids():
    import seed_data

    ids = [p["id"] for p in seed_data.seed_projects()]
    assert len(ids) == len(set(ids))


def test_seed_covers_both_creator_accounts():
    import seed_data

    creators = {p["creator"] for p in seed_data.seed_projects()}
    assert len(creators) >= 2


def test_seed_claims_no_performance_metrics():
    """We seed real titles and dates only -- never invented view counts."""
    import seed_data

    for project in seed_data.seed_projects():
        assert "views" not in project
        assert "likes" not in project
