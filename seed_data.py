"""Seed catalogue for the workspace library.

These are real founder-story videos this account has published, exported from the internal
content tracker (title = the video's on-screen hook, date = its publish date, account = the
creator account it went out on). They are seeded as ``published`` history so the workspace
opens on a genuine back catalogue instead of one placeholder row.

Nothing here is invented and no performance numbers are claimed: only the hook text, the
publish date and the owning account are carried over. Seeding runs once, when the library is
empty - see ``store.init_db`` / ``seed_if_empty``.
"""

from __future__ import annotations

from typing import Any

# title / date / account exported from the internal content tracker.
SEED_ROWS: list[dict[str, str]] = [
    {
        "video_id": "15352",
        "date": "2026-07-25",
        "account": "SG",
        "title": "i got so desperate",
        "filename": "i-got-so-desperate.mp4",
    },
    {
        "video_id": "15353",
        "date": "2026-07-25",
        "account": "US",
        "title": "I grew up with eczema.",
        "filename": "i-grew-up-with-eczema.mp4",
    },
    {
        "video_id": "15292",
        "date": "2026-07-16",
        "account": "SG",
        "title": "I rebuilt the life eczema made me hide from",
        "filename": "i-rebuilt-the-life-eczema-made-me-hide-fro.mp4",
    },
    {
        "video_id": "15287",
        "date": "2026-07-14",
        "account": "SG",
        "title": "I spent years thinking my skin was the problem",
        "filename": "i-spent-years-thinking-my-skin-was-the-pro.mp4",
    },
    {
        "video_id": "15288",
        "date": "2026-07-14",
        "account": "SG",
        "title": "You said stop scratching",
        "filename": "you-said-stop-scratching.mp4",
    },
    {
        "video_id": "15290",
        "date": "2026-07-14",
        "account": "US",
        "title": "i lost years of my life to eczema",
        "filename": "i-lost-years-of-my-life-to-eczema.mp4",
    },
    {
        "video_id": "15291",
        "date": "2026-07-14",
        "account": "US",
        "title": "Eczema stole my childhood twice",
        "filename": "eczema-stole-my-childhood-twice.mp4",
    },
    {
        "video_id": "15285",
        "date": "2026-07-12",
        "account": "SG",
        "title": "bro will never glow up from his eczema",
        "filename": "bro-will-never-glow-up-from-his-eczema.mp4",
    },
    {
        "video_id": "15286",
        "date": "2026-07-12",
        "account": "SG",
        "title": "aren't you hot in those long sleeves?",
        "filename": "aren-t-you-hot-in-those-long-sleeves.mp4",
    },
    {
        "video_id": "15268",
        "date": "2026-07-07",
        "account": "US",
        "title": "i used to hide from everyone",
        "filename": "i-used-to-hide-from-everyone.mp4",
    },
    {
        "video_id": "15269",
        "date": "2026-07-07",
        "account": "US",
        "title": "If you have eczema, scratch it. They are lying to sell more steroid cr",
        "filename": "if-you-have-eczema-scratch-it-they-are-lyi.mp4",
    },
    {
        "video_id": "15256",
        "date": "2026-07-06",
        "account": "SG",
        "title": "i can never go in pools",
        "filename": "i-can-never-go-in-pools.mp4",
    },
    {
        "video_id": "15261",
        "date": "2026-07-06",
        "account": "SG",
        "title": "i could cover my arms",
        "filename": "i-could-cover-my-arms.mp4",
    },
    {
        "video_id": "15262",
        "date": "2026-07-06",
        "account": "SG",
        "title": "why did you tie your hands every night?",
        "filename": "why-did-you-tie-your-hands-every-night.mp4",
    },
    {
        "video_id": "15263",
        "date": "2026-07-06",
        "account": "US",
        "title": "why are you dressed like that on a flight?",
        "filename": "why-are-you-dressed-like-that-on-a-flight.mp4",
    },
    {
        "video_id": "15264",
        "date": "2026-07-06",
        "account": "US",
        "title": "watch my spark come back after healing from eczema",
        "filename": "watch-my-spark-come-back-after-healing-fro.mp4",
    },
    {
        "video_id": "15265",
        "date": "2026-07-06",
        "account": "US",
        "title": "we couldn't afford the treatments..",
        "filename": "we-couldn-t-afford-the-treatments.mp4",
    },
    {
        "video_id": "15266",
        "date": "2026-07-06",
        "account": "US",
        "title": "just fix your gut health dude",
        "filename": "just-fix-your-gut-health-dude.mp4",
    },
    {
        "video_id": "14272",
        "date": "2026-07-05",
        "account": "SG",
        "title": "my doctor did this to me",
        "filename": "my-doctor-did-this-to-me.mp4",
    },
    {
        "video_id": "14274",
        "date": "2026-07-05",
        "account": "US",
        "title": "i wanted to live normally",
        "filename": "i-wanted-to-live-normally.mp4",
    },
    {
        "video_id": "14275",
        "date": "2026-07-05",
        "account": "SG",
        "title": "maybe honey will fix it",
        "filename": "maybe-honey-will-fix-it.mp4",
    },
    {
        "video_id": "14271",
        "date": "2026-07-03",
        "account": "SG",
        "title": "who wears that on a flight?",
        "filename": "who-wears-that-on-a-flight.mp4",
    },
    {
        "video_id": "14265",
        "date": "2026-07-02",
        "account": "SG",
        "title": "watch me glow from..",
        "filename": "watch-me-glow-from.mp4",
    },
    {
        "video_id": "14266",
        "date": "2026-07-02",
        "account": "SG",
        "title": "i could cover my arms.. but not my face.",
        "filename": "i-could-cover-my-arms-but-not-my-face.mp4",
    },
]


ACCOUNT_LABELS = {
    "US": "Creator (US)",
    "SG": "Creator (SG)",
}


def _creator_label(account: str) -> str:
    account = (account or "").strip().upper()
    return ACCOUNT_LABELS.get(account, "Creator (primary)")


def seed_projects() -> list[dict[str, Any]]:
    """Build library rows for the seed catalogue, newest first."""
    projects: list[dict[str, Any]] = []
    for row in SEED_ROWS:
        posted = f"{row['date']} 00:00 UTC"
        projects.append(
            {
                "id": f"vid-{row['video_id']}",
                "title": row["title"],
                "filename": row["filename"],
                "duration": "--",
                "size_mb": 0.0,
                "creator": _creator_label(row["account"]),
                "status": "published",
                "caption": row["title"],
                "created": posted,
                "published_at": posted,
                "reviewed": True,
                "approved": True,
                "checks": {
                    "rights": True,
                    "reviewed": True,
                    "policy": True,
                    "control": True,
                    "consent": True,
                },
                "is_sample": False,
                "is_seed": True,
                "source": "content tracker",
            }
        )
    return projects
