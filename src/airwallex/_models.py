from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class AirwallexModel(BaseModel):
    """Base class for all API response models.

    Instances are immutable, and unknown fields returned by newer API
    versions are preserved (accessible via attribute access) rather than
    dropped, so the SDK stays forward-compatible.
    """

    model_config = ConfigDict(
        frozen=True,
        extra="allow",
        populate_by_name=True,
    )

    def to_dict(self) -> dict[str, Any]:
        """Return the model as a plain dict, excluding unset fields."""
        return self.model_dump(exclude_unset=True, by_alias=True)


def clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Drop ``None`` values so optional query params are omitted, not sent as 'None'."""
    return {key: value for key, value in params.items() if value is not None}
