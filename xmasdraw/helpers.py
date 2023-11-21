import os
import random
import yaml

drawings_filepath = os.getenv("DRAWINGS_FILEPATH", "./drawings.yaml")


class DrawException(Exception):
    pass


def get_drawing_participants(draw_name):
    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)
    return configs.get("draws", {}).get(draw_name)


def create_draw(params):
    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)

    draws = configs.get("draws", {})
    if draws.get(params["name"]) is not None:
        raise DrawException('Draw already exists')

    draws[params["name"]] = params["participants"]
    configs['draws'] = draws

    with open(drawings_filepath, "w") as f:
        yaml.dump(configs, f)


def draw(participants, current_name):
    drawable_participants = [p for p in participants if p["name"] != current_name]
    already_drawn = [
        p["offers_to"]
        for p in drawable_participants
        if p.get("offers_to") and p.get("offers_to") != current_name
    ]
    not_drawn = set([p["name"] for p in drawable_participants]).symmetric_difference(
        set(already_drawn)
    )
    not_already_played = [
        p["name"] for p in drawable_participants if not p.get("offers_to")
    ]

    if len(not_drawn) == 0:
        raise DrawException("Not enough participants to draw")

    # Special case: if only 2 people can be picked but one of them have not
    # played yet, we need to pick him otherwise he won't have anyone to pick
    if len(not_drawn) == 2 and len(not_already_played) == 1:
        return not_already_played[0]

    return random.choice(list(not_drawn))


def store_participation(draw_name, participant_name, offers_to_name):
    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)

    for person in configs["draws"][draw_name]:
        if person.get("name") == participant_name:
            person["offers_to"] = offers_to_name

    with open(drawings_filepath, "w") as f:
        yaml.dump(configs, f)


def reset_draw(draw_name):
    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)

    for person in configs["draws"][draw_name]:
        person.pop("offers_to", None)

    with open(drawings_filepath, "w") as f:
        yaml.dump(configs, f)
