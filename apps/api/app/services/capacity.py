"""
CapacityEngine

Converts a list of TeamMember domain objects into Capacity snapshots.

Rules
-----
- available_hours = total_hours - buffer_hours
- buffer_hours    = total_hours * (buffer_percent / 100)
- buffer_percent  is read from the Config sheet key "buffer_percent"
- if the key is absent the DEFAULT_BUFFER_PERCENT is used
- the per-member reserved_buffer_percent always overrides the global default
  when it is explicitly set (non-zero)
"""

from app.connectors.sheets.schemas import ConfigRow
from app.domain import Capacity, TeamMember

DEFAULT_BUFFER_PERCENT: float = 25.0
_CONFIG_KEY = "buffer_percent"


def _resolve_buffer_percent(
    member: TeamMember,
    global_buffer: float,
) -> float:
    """
    Return the effective buffer percent for one member.

    Priority:
    1. member.reserved_buffer_percent  if it is non-zero
    2. global_buffer from config / default
    """
    if member.reserved_buffer_percent != 0:
        return member.reserved_buffer_percent
    return global_buffer


def _parse_global_buffer(config_rows: list[ConfigRow]) -> float:
    """Extract buffer_percent from ConfigRow list; return default if absent or invalid."""
    for row in config_rows:
        if row.key.strip().lower() == _CONFIG_KEY:
            try:
                value = float(row.value)
                if 0 <= value <= 100:
                    return value
            except (ValueError, TypeError):
                pass
    return DEFAULT_BUFFER_PERCENT


class CapacityEngine:
    """
    Deterministic capacity calculator.

    Usage::

        engine = CapacityEngine(config_rows)
        capacities = engine.build(team_members)
    """

    def __init__(self, config_rows: list[ConfigRow] | None = None) -> None:
        self._global_buffer = _parse_global_buffer(config_rows or [])

    def build(self, members: list[TeamMember]) -> list[Capacity]:
        """Return one Capacity per TeamMember in the same order."""
        return [self._build_one(member) for member in members]

    def _build_one(self, member: TeamMember) -> Capacity:
        buf_pct = _resolve_buffer_percent(member, self._global_buffer)
        total = member.weekly_capacity_hours
        buffer = round(total * buf_pct / 100, 10)
        available = round(total - buffer, 10)
        return Capacity(
            member_name=member.name,
            total_hours=total,
            buffer_hours=buffer,
            available_hours=available,
        )
