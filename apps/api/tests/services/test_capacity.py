"""
Tests for CapacityEngine.

Covers:
- Default buffer (25%) when no config rows present
- Config-driven buffer from ConfigRow list
- Per-member reserved_buffer_percent overrides global default
- Zero-capacity edge case
- Ordering preserved
- Invalid config value falls back to default
"""

import pytest
from app.connectors.sheets.schemas import ConfigRow
from app.domain import TeamMember
from app.services.capacity import DEFAULT_BUFFER_PERCENT, CapacityEngine


# ─────────────────────────────── helpers


def _member(name: str, hours: float, buffer_pct: float = 0) -> TeamMember:
    return TeamMember(
        name=name,
        weekly_capacity_hours=hours,
        reserved_buffer_percent=buffer_pct,
    )


def _config_row(key: str, value: str) -> ConfigRow:
    return ConfigRow.model_validate({"Key": key, "Value": value})


# ─────────────────────────────── default buffer


def test_default_buffer_is_25_percent_when_no_config() -> None:
    engine = CapacityEngine()
    caps = engine.build([_member("Ivan", 40)])

    assert caps[0].buffer_hours == pytest.approx(10.0)
    assert caps[0].available_hours == pytest.approx(30.0)


def test_default_buffer_percent_constant_value() -> None:
    assert DEFAULT_BUFFER_PERCENT == 25.0


def test_empty_team_returns_empty_list() -> None:
    assert CapacityEngine().build([]) == []


# ─────────────────────────────── config-driven buffer


def test_config_buffer_overrides_default() -> None:
    config = [_config_row("buffer_percent", "20")]
    engine = CapacityEngine(config)
    caps = engine.build([_member("Ivan", 40)])

    assert caps[0].buffer_hours == pytest.approx(8.0)
    assert caps[0].available_hours == pytest.approx(32.0)


def test_config_key_is_case_insensitive() -> None:
    config = [_config_row("Buffer_Percent", "10")]
    engine = CapacityEngine(config)
    caps = engine.build([_member("Ivan", 20)])

    assert caps[0].buffer_hours == pytest.approx(2.0)


def test_invalid_config_value_falls_back_to_default() -> None:
    config = [_config_row("buffer_percent", "not-a-number")]
    engine = CapacityEngine(config)
    caps = engine.build([_member("Ivan", 40)])

    # should fall back to 25%
    assert caps[0].buffer_hours == pytest.approx(10.0)


def test_out_of_range_config_value_falls_back_to_default() -> None:
    config = [_config_row("buffer_percent", "150")]
    engine = CapacityEngine(config)
    caps = engine.build([_member("Ivan", 40)])

    assert caps[0].buffer_hours == pytest.approx(10.0)


def test_zero_buffer_config_is_accepted() -> None:
    config = [_config_row("buffer_percent", "0")]
    engine = CapacityEngine(config)
    caps = engine.build([_member("Ivan", 40)])

    assert caps[0].buffer_hours == pytest.approx(0.0)
    assert caps[0].available_hours == pytest.approx(40.0)


# ─────────────────────────────── per-member override


def test_member_reserved_buffer_overrides_global() -> None:
    config = [_config_row("buffer_percent", "25")]
    engine = CapacityEngine(config)
    # member sets 10% explicitly
    caps = engine.build([_member("Maria", 40, buffer_pct=10)])

    assert caps[0].buffer_hours == pytest.approx(4.0)
    assert caps[0].available_hours == pytest.approx(36.0)


def test_member_zero_reserved_buffer_uses_global() -> None:
    """reserved_buffer_percent=0 means 'use global'; it is not a 0% override."""
    config = [_config_row("buffer_percent", "20")]
    engine = CapacityEngine(config)
    caps = engine.build([_member("Ivan", 40, buffer_pct=0)])

    # 0 means use global (20%)
    assert caps[0].buffer_hours == pytest.approx(8.0)


# ─────────────────────────────── capacity model fields


def test_capacity_member_name_preserved() -> None:
    caps = CapacityEngine().build([_member("Алиса", 32)])
    assert caps[0].member_name == "Алиса"


def test_capacity_total_hours_preserved() -> None:
    caps = CapacityEngine().build([_member("Борис", 20)])
    assert caps[0].total_hours == pytest.approx(20.0)


def test_capacity_buffer_percent_computed() -> None:
    config = [_config_row("buffer_percent", "25")]
    caps = CapacityEngine(config).build([_member("Ivan", 40)])
    assert caps[0].buffer_percent == pytest.approx(25.0)


# ─────────────────────────────── ordering


def test_output_order_matches_input_order() -> None:
    members = [_member("C", 40), _member("A", 32), _member("B", 24)]
    caps = CapacityEngine().build(members)
    assert [c.member_name for c in caps] == ["C", "A", "B"]


# ─────────────────────────────── multiple members


def test_multiple_members_each_get_own_capacity() -> None:
    members = [_member("Ivan", 40), _member("Maria", 32, buffer_pct=10)]
    config = [_config_row("buffer_percent", "25")]
    caps = CapacityEngine(config).build(members)

    assert len(caps) == 2
    assert caps[0].available_hours == pytest.approx(30.0)  # 40 * 0.75
    assert caps[1].available_hours == pytest.approx(28.8)  # 32 * 0.90


# ─────────────────────────────── zero capacity edge case


def test_zero_weekly_capacity_produces_zero_available() -> None:
    caps = CapacityEngine().build([_member("Ghost", 0)])
    assert caps[0].available_hours == pytest.approx(0.0)
    assert caps[0].buffer_hours == pytest.approx(0.0)
