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
        return not_already_played[0]["name"]

    return random.choice(not_drawn)["name"]


def store_participation(draw_name, participant_name, offers_to_name):
    with open(DRAWINGS_FILEPATH) as f:
        drawings = yaml.safe_load(f)

    for person in drawings[draw_name]:
        if person.get("name") == participant_name:
            person["offers_to"] = offers_to_name
        elif person.get("name") == offers_to_name:
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


def can_reset(draw_name, username, password):
    with open(DRAWINGS_FILEPATH) as f:
        drawings = yaml.safe_load(f)

    can_reset = [
        p
        for p in drawings[draw_name]
        if p.get("reset_password", None)
        and p["name"] == username
        and p["reset_password"] == password
    ]

    return len(can_reset) > 0
