import os
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

os.environ.setdefault("SANDBOX_TIKTOK_CLIENT_KEY", "sandbox-key")
os.environ.setdefault("SANDBOX_TIKTOK_CLIENT_SECRET", "sandbox-secret")
os.environ.setdefault("SANDBOX_TIKTOK_SESSION_SECRET", "sandbox-session-secret-for-tests")
os.environ.setdefault("EM_POSTING_COOKIE_SECURE", "false")
os.environ.setdefault("EM_POSTING_SESSION_STORE", "/tmp/em-posting-test-sessions.json")

import tiktok_integration as ti
from server import app


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
    ti._sessions["session-2"] = ti.TikTokSession(
        access_token="access-token",
        refresh_token="refresh-token",
        open_id="open-id",
        scopes="user.info.basic,video.upload",
        profile={"display_name": "Reuben"},
    )
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
    ti._sessions["session-3"] = ti.TikTokSession(
        access_token="access-token",
        refresh_token="refresh-token",
        open_id="open-id",
        scopes="user.info.basic",
        profile={},
    )
    client = TestClient(app)
    response = client.post(
        "/api/tiktok/upload",
        cookies={ti.SESSION_COOKIE: signed_session_cookie("session-3")},
        files={"video": ("sample.mp4", b"fake-mp4-data", "video/mp4")},
    )
    assert response.status_code == 403
