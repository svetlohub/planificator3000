import pytest
from app.domain import Capacity, TeamMember
from pydantic import ValidationError


def test_team_member_computed_capacity(team_member: TeamMember) -> None:
    assert team_member.skills == ["python", "planning"]
    assert team_member.buffer_hours == 8
    assert team_member.available_capacity_hours == 32


def test_team_member_rejects_duplicate_skills() -> None:
    with pytest.raises(ValidationError, match="skills must be unique"):
        TeamMember(
            name="Alex",
            weekly_capacity_hours=40,
            reserved_buffer_percent=10,
            skills=["Python", "python"],
        )


def test_capacity_validates_available_hours() -> None:
    capacity = Capacity(member_name="Alex", total_hours=40, buffer_hours=8, available_hours=32)

    assert capacity.buffer_percent == 20


def test_capacity_rejects_inconsistent_available_hours() -> None:
    with pytest.raises(ValidationError, match="available_hours"):
        Capacity(member_name="Alex", total_hours=40, buffer_hours=8, available_hours=30)
