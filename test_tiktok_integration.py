import ast
import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

os.environ.setdefault("SANDBOX_TIKTOK_CLIENT_KEY", "sandbox-key")
os.environ.setdefault("SANDBOX_TIKTOK_CLIENT_SECRET", "sandbox-secret")
os.environ.setdefault("SANDBOX_TIKTOK_SESSION_SECRET", "sandbox-session-secret-for-tests")
os.environ.setdefault("EM_POSTING_COOKIE_SECURE", "false")
os.environ.setdefault("EM_POSTING_SESSION_STORE", "/tmp/em-posting-test-sessions.json")

import tiktok_integration as ti
from server import app


def test_empty_queue_is_hidden_when_receipt_exists():
    module = ast.parse(Path("app.py").read_text())
    helper = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "should_show_empty_queue"
    )
    namespace = {}
    exec(compile(ast.Module(body=[helper], type_ignores=[]), "app.py", "exec"), namespace)
    should_show = namespace["should_show_empty_queue"]
    assert should_show([], None) is True
    assert should_show([], {"Publish ID": "v_inbox_file~123"}) is False
    assert should_show([{"title": "post"}], None) is False


def load_app_helpers(*names):
    module = ast.parse(Path("app.py").read_text())
    helpers = [
        node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    namespace = {}
    exec(compile(ast.Module(body=helpers, type_ignores=[]), "app.py", "exec"), namespace)
    return namespace


def test_duplicate_approval_detects_same_asset_only():
    helper = load_app_helpers("is_duplicate_approval")["is_duplicate_approval"]
    queue = [{"fingerprint": "first"}]
    assert helper(queue, {"fingerprint": "first"}) is True
    assert helper(queue, {"fingerprint": "second"}) is False


def test_existing_queue_duplicates_are_collapsed():
    helper = load_app_helpers("deduplicate_queue")["deduplicate_queue"]
    queue = [
        {"fingerprint": "same", "approved_at": "newer"},
        {"fingerprint": "same", "approved_at": "older"},
        {"fingerprint": "different", "approved_at": "other"},
    ]
    assert helper(queue) == [queue[0], queue[2]]


def test_tiktok_status_copy_does_not_claim_inbox_before_delivery():
    helper = load_app_helpers("tiktok_status_copy")["tiktok_status_copy"]
    _, processing = helper("PROCESSING_UPLOAD")
    delivered_title, delivered = helper("SEND_TO_USER_INBOX")
    failed_title, failed = helper("FAILED", "frame_rate_check_failed")
    assert "No inbox notification is expected yet" in processing
    assert delivered_title == "Inbox notification sent"
    assert "creator inbox notification was delivered" in delivered
    assert failed_title == "TikTok processing failed"
    assert "frame_rate_check_failed" in failed


class FakeResponse:
    def __init__(self, payload=None, status_code=200):
        self._payload = payload or {}
        self.status_code = status_code
        self.is_error = status_code >= 400

    def json(self):
        return self._payload


class FakeAsyncClient:
    def __init__(self, *, post_responses=None, get_responses=None, put_responses=None, **kwargs):
        self.post_responses = list(post_responses or [])
        self.get_responses = list(get_responses or [])
        self.put_responses = list(put_responses or [])

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def post(self, *args, **kwargs):
        return self.post_responses.pop(0)

    async def get(self, *args, **kwargs):
        return self.get_responses.pop(0)

    async def put(self, *args, **kwargs):
        return self.put_responses.pop(0)


def signed_session_cookie(session_id):
    return ti._serializer().dumps(session_id)


def make_session(session_id, scopes="user.info.basic,video.upload"):
    ti._sessions[session_id] = ti.TikTokSession(
        access_token="access-token",
        refresh_token="refresh-token",
        open_id="open-id",
        scopes=scopes,
        profile={"display_name": "Reuben"},
    )


def test_login_sets_state_cookie_and_requests_narrow_scopes():
    client = TestClient(app)
    response = client.get("/auth/tiktok/login", follow_redirects=False)
    assert response.status_code == 302
    assert "scope=user.info.basic%2Cvideo.upload" in response.headers["location"]
    assert "redirect_uri=https%3A%2F%2Ftiktok-posting.onrender.com%2Fauth%2Ftiktok%2Fcallback%2F" in response.headers["location"]
    assert ti.OAUTH_COOKIE in response.cookies


def test_session_status_exposes_profile_not_tokens():
    ti._sessions["session-1"] = ti.TikTokSession(
        access_token="do-not-expose",
        refresh_token="also-secret",
        open_id="open-id",
        scopes="user.info.basic,video.upload",
        profile={"display_name": "Reuben", "avatar_url": "https://example.com/a.jpg"},
    )
    client = TestClient(app)
    response = client.get("/api/tiktok/session", cookies={ti.SESSION_COOKIE: signed_session_cookie("session-1")})
    assert response.status_code == 200
    assert response.json()["profile"]["display_name"] == "Reuben"
    assert "do-not-expose" not in response.text


def test_upload_initializes_and_transfers_mp4():
    make_session("session-2")
    fake_client = FakeAsyncClient(
        post_responses=[FakeResponse({"data": {"publish_id": "v_inbox_file~123", "upload_url": "https://upload.example/video"}, "error": {"code": "ok", "message": ""}})],
        put_responses=[FakeResponse(status_code=201)],
    )
    with patch.object(ti.httpx, "AsyncClient", return_value=fake_client):
        client = TestClient(app)
        response = client.post(
            "/api/tiktok/upload",
            cookies={ti.SESSION_COOKIE: signed_session_cookie("session-2")},
            files={"video": ("sample.mp4", b"fake-mp4-data", "video/mp4")},
        )
    assert response.status_code == 200
    assert response.json()["publish_id"] == "v_inbox_file~123"
    assert response.json()["destination"] == "TikTok draft/inbox"


def test_upload_requires_video_upload_scope():
    make_session("session-3", scopes="user.info.basic")
    client = TestClient(app)
    response = client.post(
        "/api/tiktok/upload",
        cookies={ti.SESSION_COOKIE: signed_session_cookie("session-3")},
        files={"video": ("sample.mp4", b"fake-mp4-data", "video/mp4")},
    )
    assert response.status_code == 403


def test_status_returns_tiktok_processing_state():
    make_session("session-4")
    fake_client = FakeAsyncClient(
        post_responses=[FakeResponse({"data": {"status": "PROCESSING_UPLOAD"}, "error": {"code": "ok", "message": ""}})],
    )
    with patch.object(ti.httpx, "AsyncClient", return_value=fake_client):
        client = TestClient(app)
        response = client.get(
            "/api/tiktok/status/v_inbox_file~123",
            cookies={ti.SESSION_COOKIE: signed_session_cookie("session-4")},
        )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "PROCESSING_UPLOAD"


def test_status_error_is_not_reported_as_success():
    make_session("session-5")
    fake_client = FakeAsyncClient(
        post_responses=[FakeResponse({"data": {}, "error": {"code": "invalid_publish_id", "message": "Unknown publish ID"}})],
    )
    with patch.object(ti.httpx, "AsyncClient", return_value=fake_client):
        client = TestClient(app)
        response = client.get(
            "/api/tiktok/status/bad-id",
            cookies={ti.SESSION_COOKIE: signed_session_cookie("session-5")},
        )
    assert response.status_code == 502
    assert response.json()["detail"] == "Unknown publish ID"
