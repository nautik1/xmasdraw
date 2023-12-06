from ..helpers import draw
from .names import BORING_NAMES


def test_never_pick_yourself():
    participants = [{"name": name} for name in BORING_NAMES[:2]]
    for i in range(99999):  # Beat the odds!
        assert draw(participants, participants[0]["name"]) == participants[1]["name"]


def test_last_participant_needs_to_have_someone_to_pick():
    participants = [
        {
            "name": "toto",
        },
        {
            "name": "titi",
            "offers_to": "toto",
        },
        {
            "name": "tata",
        },
    ]

    for i in range(99999):  # beat the odds
        drawn = draw(participants, "toto")
        assert drawn == "tata"
