"""
database.py — MVP in-memory profile store.

Stores profiles as a dict keyed by profile_id (UUID string).
All four CRUD operations are implemented as pure functions with no side effects
embedded in API routes.

Post-MVP: replace the dict with async SQLAlchemy sessions.
"""
from __future__ import annotations

import uuid
from typing import Any

from backend.app.agents.profile_agent import StudentProfile

# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------
_profiles: dict[str, StudentProfile] = {}


def save_profile(profile: StudentProfile) -> str:
    """Persist a new profile and return its generated UUID.

    Args:
        profile: A validated StudentProfile instance.

    Returns:
        The newly assigned profile_id string (UUID4).
    """
    profile_id = str(uuid.uuid4())
    _profiles[profile_id] = profile
    return profile_id


def get_profile(profile_id: str) -> StudentProfile | None:
    """Retrieve a profile by its ID.

    Args:
        profile_id: The UUID string assigned at creation.

    Returns:
        The StudentProfile if found, otherwise None.
    """
    return _profiles.get(profile_id)


def update_profile(profile_id: str, updates: dict[str, Any]) -> StudentProfile | None:
    """Apply a partial update to an existing profile.

    Only keys present in *updates* are changed. Unknown keys are silently
    ignored (Pydantic model_copy handles field validation).

    Args:
        profile_id: The UUID of the profile to update.
        updates: Dict of field names and their new values.

    Returns:
        The updated StudentProfile, or None if the profile was not found.
    """
    existing = _profiles.get(profile_id)
    if existing is None:
        return None
    updated = existing.model_copy(update=updates)
    _profiles[profile_id] = updated
    return updated


def delete_profile(profile_id: str) -> bool:
    """Remove a profile from the store.

    Args:
        profile_id: The UUID of the profile to delete.

    Returns:
        True if the profile was found and deleted, False if not found.
    """
    if profile_id not in _profiles:
        return False
    del _profiles[profile_id]
    return True


def clear_all() -> None:
    """Remove every profile from the store.

    Used only by tests to reset state between test runs.
    """
    _profiles.clear()
