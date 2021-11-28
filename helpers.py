import yaml
import random

DRAWINGS_FILEPATH = "drawings.yaml"


def get_drawing_participants(draw_name):
    with open(DRAWINGS_FILEPATH) as f:
        drawings = yaml.safe_load(f)
    return drawings.get(draw_name)


def draw(participants):
    not_drawn = [p for p in participants if not p.get("drawn")]
    not_already_played = [p for p in not_drawn if not p.get("offers_to")]

    # Special case: if only 2 people can be picked but one of them have not
    # played yet, we need to pick him otherwise he won't have anyone to pick
    if len(not_drawn) == 2 and len(not_already_played) == 1:
        return not_already_played[0]

    return random.choice(not_drawn)


def store_participation(draw_name, participant, offers_to):
    with open(DRAWINGS_FILEPATH) as f:
        drawings = yaml.safe_load(f)

    for person in drawings[draw_name]:
        if person.get("name") == participant.get("name"):
            person["offers_to"] = offers_to.get("name")
        elif person.get("name") == offers_to.get("name"):
            person["drawn"] = True

    with open(DRAWINGS_FILEPATH, "w") as f:
        yaml.dump(drawings, f)


def reset_draw(draw_name):
    with open(DRAWINGS_FILEPATH) as f:
        drawings = yaml.safe_load(f)

    for person in drawings[draw_name]:
        person.pop("offers_to", None)
        person.pop("drawn", None)

    with open(DRAWINGS_FILEPATH, "w") as f:
        yaml.dump(drawings, f)


def can_reset(draw_name, user_name):
    with open(DRAWINGS_FILEPATH) as f:
        drawings = yaml.safe_load(f)

    can_reset = [
        p
        for p in drawings[draw_name]
        if p.get("can_reset", None) and p["name"] == user_name
    ]

    return len(can_reset) > 0
