"""ID generation utility for creating unique identifiers."""

import uuid


def create_id() -> str:
    """Generate a unique ID string."""
    return str(uuid.uuid4())
