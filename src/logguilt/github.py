"""Post apologetic comments to GitHub issues and pull requests.

Uses :mod:`urllib` so the project has no hard dependency on a GitHub SDK.
The token is resolved from ``GitHubOptions.token`` or the ``GITHUB_TOKEN`` /
``GH_TOKEN`` environment variables.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .models import CommentPayload, GuiltScore, Incident, Poem

API_ROOT = "https://api.github.com"
TOKEN_ENV_VARS = ("GITHUB_TOKEN", "GH_TOKEN")
USER_AGENT = "logguilt/1.0"


class GitHubError(RuntimeError):
    """Raised when the GitHub API rejects a comment request."""


@dataclass
class GitHubOptions:
    """Settings controlling where and how comments are posted."""

    repo: str
    number: int
    token: Optional[str] = None
    api_root: str = API_ROOT
    dry_run: bool = False
    timeout: float = 10.0


def resolve_token(options: GitHubOptions) -> Optional[str]:
    """Return the token from options or the environment, if any."""
    if options.token:
        return options.token
    for name in TOKEN_ENV_VARS:
        value = os.environ.get(name)
        if value:
            return value
    return None


def render_body(incident: Incident, poem: Poem, score: GuiltScore) -> str:
    """Compose the apologetic comment body for an incident."""
    return "\n".join(
        [
            f"🙇 Apologies from the **{incident.category}** team.",
            "",
            f"Our guilt meter reads **{score.total:.0f}/100** ({score.label}).",
            "",
            f"Offending pattern: `{incident.summary}`",
            f"Occurrences: {incident.count}",
            "",
            poem.text,
            "",
            "_— LogGuilt, writing on behalf of everyone who paged you_",
        ]
    )


def build_comment(
    incident: Incident,
    poem: Poem,
    score: GuiltScore,
    *,
    repo: str,
    number: int,
    kind: str = "issue",
) -> CommentPayload:
    """Build a :class:`CommentPayload` ready for posting."""
    return CommentPayload(
        repo=repo,
        number=number,
        body=render_body(incident, poem, score),
        kind=kind,
    )


class GitHubClient:
    """Minimal GitHub REST client for posting comments."""

    def __init__(self, options: GitHubOptions) -> None:
        self.options = options

    def endpoint(self, payload: CommentPayload) -> str:
        """Return the comments endpoint URL for the given payload."""
        kind = str(getattr(payload, "kind", "")).lower()
        segment = "pulls" if kind in {"pr", "pull", "pull_request"} else "issues"
        return (
            f"{self.options.api_root}/repos/{payload.repo}"
            f"/{segment}/{payload.number}/comments"
        )

    def post(self, payload: CommentPayload) -> Dict[str, Any]:
        """Post ``payload.body`` and return the parsed API response."""
        if self.options.dry_run:
            return {
                "dry_run": True,
                "url": self.endpoint(payload),
                "body": payload.body,
            }

        token = resolve_token(self.options)
        if not token:
            raise GitHubError(
                "No GitHub token found; set GITHUB_TOKEN or GH_TOKEN"
            )

        request = urllib.request.Request(
            self.endpoint(payload),
            data=json.dumps({"body": payload.body}).encode("utf-8"),
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(
                request, timeout=self.options.timeout
            ) as response:
                raw = response.read().decode("utf-8")
                status = response.status
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")
            raise GitHubError(
                f"GitHub API returned {exc.code} for "
                f"{payload.repo}#{payload.number}: {detail}"
            ) from exc
        except urllib.error.URLError as exc:
            raise GitHubError(f"Could