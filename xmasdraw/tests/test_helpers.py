import pytest

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


@pytest.mark.parametrize("nb_of_participants", range(3, len(BORING_NAMES)))
def test_dumb_draw_until_done(nb_of_participants):
    participants = [{"name": name} for name in BORING_NAMES[:nb_of_participants]]

    already_drawn = []
    for player in participants:
        player_name = player["name"]
        drawn = draw(participants, player_name)

        assert drawn not in already_drawn
        assert drawn != player_name

        # Take draw into account for next round
        already_drawn.append(drawn)
        for p in participants:
            if p["name"] == player_name:
                p["offers_to"] = drawn
