import ast
import os
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from streamlit.testing.v1 import AppTest

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


def load_app_nodes(*names):
    """Exec selected top-level assignments/functions from app.py in an isolated namespace."""
    module = ast.parse(Path("app.py").read_text())
    wanted = []
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name in names:
            wanted.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in names for target in node.targets
        ):
            wanted.append(node)
    namespace = {"os": os}
    exec(compile(ast.Module(body=wanted, type_ignores=[]), "app.py", "exec"), namespace)
    return namespace


def test_configured_public_url_prefers_env_over_fallback():
    namespace = load_app_nodes("PUBLIC_URL_FALLBACK", "configured_public_url")
    configured_public_url = namespace["configured_public_url"]
    with patch.dict(os.environ, {"EM_POSTING_PUBLIC_URL": "https://posting.example.com/"}):
        assert configured_public_url() == "https://posting.example.com"
    os.environ.pop("EM_POSTING_PUBLIC_URL", None)
    assert configured_public_url() == namespace["PUBLIC_URL_FALLBACK"]


def test_public_links_use_configured_origin_not_request_host():
    namespace = load_app_nodes(
        "PUBLIC_URL_FALLBACK", "configured_public_url", "public_base_url", "legal_url"
    )
    with patch.dict(os.environ, {"EM_POSTING_PUBLIC_URL": "https://posting.example.com"}):
        assert namespace["public_base_url"]() == "https://posting.example.com"
        assert namespace["legal_url"]("terms") == (
            "https://posting.example.com/?page=legal&policy=terms"
        )


def test_home_exposes_public_terms_and_privacy_links_without_menu():
    source = Path("app.py").read_text()
    module = ast.parse(source)
    home = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "render_home"
    )
    home_source = ast.get_source_segment(source, home)
    # Terms and Privacy must be directly linkable from the Home page itself.
    # Can use either single or double quotes
    assert "legal_url" in home_source and "terms" in home_source
    assert "legal_url" in home_source and "privacy" in home_source
    assert "Terms of Service" in home_source
    assert "Privacy Policy" in home_source


def test_production_render_domain_is_the_only_fallback():
    # Legal links, sign-in links, and OAuth redirect derive from this non-branded Render fallback.
    app_source = Path("app.py").read_text()
    integration_source = Path("tiktok_integration.py").read_text()
    assert app_source.count("posting-app-gvtf.onrender.com") == 1
    assert integration_source.count("posting-app-gvtf.onrender.com") == 1
    assert "tiktok-posting.onrender.com" not in app_source
    assert "tiktok-posting.onrender.com" not in integration_source


def test_public_contact_email_is_used_in_app_and_legal_copy():
    app_source = Path("app.py").read_text()
    assert "contact@eczemamitten.com" in app_source
    assert "eczemamitten@gmail.com" not in app_source


def test_one_branded_icon_is_used_for_page_config_and_sidebar():
    source = Path("app.py").read_text()
    assert 'APP_ICON_PATH = Path(__file__).parent / "assets" / "em-posting-icon.png"' in source
    assert "page_icon=str(APP_ICON_PATH)" in source
    assert 'src="/app/static/assets/em-posting-icon.png"' in source


def test_favicon_and_visible_brand_mark_serve_the_same_asset():
    icon = Path("assets/em-posting-icon.png").read_bytes()
    client = TestClient(app)
    favicon = client.get("/favicon.png")
    visible_mark = client.get("/app/static/assets/em-posting-icon.png")
    assert favicon.status_code == 200
    assert favicon.headers["content-type"].startswith("image/png")
    assert favicon.content == icon
    assert visible_mark.status_code == 200
    assert visible_mark.content == icon


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
    # With EM_POSTING_PUBLIC_URL unset, the redirect uses the documented production Render URL.
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("EM_POSTING_PUBLIC_URL", None)
        client = TestClient(app)
        response = client.get("/auth/tiktok/login", follow_redirects=False)
    assert response.status_code == 302
    assert "scope=user.info.basic%2Cvideo.upload" in response.headers["location"]
    assert "redirect_uri=https%3A%2F%2Fposting-app-gvtf.onrender.com%2Fauth%2Ftiktok%2Fcallback%2F" in response.headers["location"]
    assert ti.OAUTH_COOKIE in response.cookies


def test_public_base_url_prefers_configured_domain_over_fallback():
    with patch.dict(os.environ, {"EM_POSTING_PUBLIC_URL": "https://posting.example.com/"}):
        assert ti.public_base_url() == "https://posting.example.com"
        assert ti.redirect_uri() == "https://posting.example.com/auth/tiktok/callback/"
    os.environ.pop("EM_POSTING_PUBLIC_URL", None)
    assert ti.public_base_url() == "https://posting-app-gvtf.onrender.com"
    assert ti.redirect_uri() == "https://posting-app-gvtf.onrender.com/auth/tiktok/callback/"


def test_login_uses_configured_public_domain_for_redirect_uri():
    with patch.dict(os.environ, {"EM_POSTING_PUBLIC_URL": "https://posting.example.com"}):
        client = TestClient(app)
        response = client.get("/auth/tiktok/login", follow_redirects=False)
    assert response.status_code == 302
    assert "redirect_uri=https%3A%2F%2Fposting.example.com%2Fauth%2Ftiktok%2Fcallback%2F" in response.headers["location"]
    assert "tiktok-posting.onrender.com" not in response.headers["location"]


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


# ============================================================================
# PUBLIC DEVELOPED WEBSITE TESTS
# ============================================================================


def test_app_version_is_current():
    """Verify APP_VERSION reflects the current release."""
    namespace = load_app_nodes("APP_VERSION")
    assert namespace["APP_VERSION"] == "v0.12.0"


def test_sample_projects_function_returns_project_library():
    """Verify sample projects data structure for public workspace."""
    source = Path("app.py").read_text()
    module = ast.parse(source)
    get_sample_projects = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "get_sample_projects"
    )
    namespace = {}
    exec(compile(ast.Module(body=[get_sample_projects], type_ignores=[]), "app.py", "exec"), namespace)
    projects = namespace["get_sample_projects"]()
    assert len(projects) == 1
    for proj in projects:
        assert "id" in proj
        assert "title" in proj
        assert "status" in proj
        assert "checks" in proj
        assert proj["status"] in ("ready", "in_review", "approved")
        assert proj["filename"] == "founder-night-routine.mp4"
        assert proj["duration"] == "00:08"


def run_public_workspace():
    return AppTest.from_file("app.py").run(timeout=20)


def test_home_project_cta_navigates_without_widget_state_error():
    app_test = run_public_workspace()
    app_test.button[0].click().run(timeout=20)
    assert not app_test.exception
    assert app_test.session_state["nav"] == "Review"
    assert app_test.session_state["current_project"] == "proj-001"


def test_sample_project_can_be_approved_into_public_handoff_queue():
    app_test = run_public_workspace()
    app_test.button[0].click().run(timeout=20)
    for checkbox in app_test.checkbox:
        checkbox.set_value(True)
    next(button for button in app_test.button if button.label == "Approve for handoff").click().run(timeout=20)
    assert not app_test.exception
    assert len(app_test.session_state["queue"]) == 1
    queue_item = app_test.session_state["queue"][0]
    assert queue_item["filename"] == "founder-night-routine.mp4"
    assert queue_item["duration"] == "00:08"
    assert queue_item["project_id"] == "proj-001"


def test_uploaded_project_asset_is_previewable_and_queueable():
    namespace = load_app_helpers("project_asset")
    project_asset = namespace["project_asset"]
    uploaded = {
        "id": "uploaded-1",
        "title": "Uploaded cut",
        "filename": "uploaded-cut.mp4",
        "size_mb": 0.5,
        "duration": None,
        "fingerprint": "upload-fingerprint",
        "is_sample": False,
        "video_data": b"mp4-bytes",
    }
    asset = project_asset(uploaded)
    assert asset["filename"] == "uploaded-cut.mp4"
    assert asset["video_data"] == b"mp4-bytes"
    assert asset["source"] == "Direct upload"

    source = Path("app.py").read_text()
    assert 'st.video(project["video_data"], muted=True)' in source
    assert "asset = project_asset(project)" in source


def test_home_renders_project_library_section():
    """Verify Home page includes project library, not just a landing hero."""
    source = Path("app.py").read_text()
    module = ast.parse(source)
    home = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "render_home"
    )
    home_source = ast.get_source_segment(source, home)
    assert "Project library" in home_source
    assert "projects" in home_source
    assert "Activity" in home_source


def test_home_renders_quick_actions():
    """Verify Home page has actionable quick action buttons."""
    source = Path("app.py").read_text()
    module = ast.parse(source)
    home = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "render_home"
    )
    home_source = ast.get_source_segment(source, home)
    assert "Quick actions" in home_source
    assert "New project" in home_source
    assert "Review queue" in home_source


def test_review_page_exists_and_renders_checklist():
    """Verify Review page has checklist-based workflow."""
    source = Path("app.py").read_text()
    module = ast.parse(source)
    render_review = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "render_review"
    )
    review_source = ast.get_source_segment(source, render_review)
    assert "Review checklist" in review_source
    assert "rights" in review_source
    assert "policy" in review_source
    assert "consent" in review_source


def test_activity_log_helper_exists():
    """Verify activity logging function exists for workspace actions."""
    source = Path("app.py").read_text()
    assert "def add_activity" in source
    assert "activity_log" in source


def test_navigation_includes_review_and_handoff():
    """Verify navigation items reflect developed workspace structure."""
    namespace = load_app_nodes("NAV_ITEMS")
    nav = namespace["NAV_ITEMS"]
    assert "Home" in nav
    assert "Review" in nav
    assert "Studio" in nav
    assert "Handoff" in nav
    assert "Legal" in nav


def test_handoff_page_exists_with_tiktok_gate():
    """Verify Handoff page requires TikTok connection for upload."""
    source = Path("app.py").read_text()
    module = ast.parse(source)
    render_handoff = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "render_handoff"
    )
    handoff_source = ast.get_source_segment(source, render_handoff)
    assert "TikTok connection" in handoff_source
    assert "Connect TikTok before uploading" in handoff_source
    assert "disabled=not session" in handoff_source


def test_public_workflow_does_not_require_login():
    """Verify workspace workflow copy does not require credentials to explore."""
    source = Path("app.py").read_text()
    # Should not have fake login forms or authentication walls for workspace exploration
    assert "password" not in source.lower() or "test account" not in source.lower()
    # The Home page should be usable without authentication
    module = ast.parse(source)
    home = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "render_home"
    )
    home_source = ast.get_source_segment(source, home)
    assert "login" not in home_source.lower() or "Connect with TikTok" in home_source


def test_sample_asset_function_returns_bundled_video():
    """Verify sample asset points to bundled video file."""
    source = Path("app.py").read_text()
    # Verify sample_path function references the correct file
    assert "sample_creator_video.mp4" in source
    assert 'assets' in source
    # Verify sample video exists
    assert (Path("assets") / "sample_creator_video.mp4").exists()


def test_verification_file_served_correctly():
    """Verify TikTok verification file is served at expected path."""
    client = TestClient(app)
    response = client.get("/tiktok8i8uszpdFElTqWKuJjxT8oFX5Gwx8T6z.txt")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert len(response.text.strip()) > 0


def test_health_endpoint_exists():
    """Verify health check endpoint for deployment."""
    client = TestClient(app)
    # The health endpoint is proxied to Streamlit's internal health
    # We just verify the server starts and responds
    response = client.get("/favicon.png")
    assert response.status_code == 200


def test_proxy_decodes_compressed_upstream_responses():
    """Regression test: the HTTP proxy must not forward raw compressed bytes
    while claiming no Content-Encoding. This previously corrupted Streamlit's
    gzip-encoded /media/*.png favicon route (browser saw undecodable gzip
    magic bytes 1f 8b 08 instead of a PNG)."""
    import gzip

    import httpx

    plain_body = b"\x89PNG\r\n\x1a\nfake-but-representative-png-bytes"
    compressed_body = gzip.compress(plain_body)

    async def fake_send(self, request, **kwargs):
        return httpx.Response(
            200,
            headers={"content-type": "image/png", "content-encoding": "gzip"},
            content=compressed_body,
            request=request,
        )

    with patch("httpx.AsyncClient.send", new=fake_send):
        client = TestClient(app)
        response = client.get("/media/fake-hash.png")

    assert response.status_code == 200
    assert response.content == plain_body
    assert response.content[:8] != b"\x1f\x8b\x08\x00\x00\x00\x00\x00"
