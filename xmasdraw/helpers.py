import os
import random
import yaml

drawings_filepath = os.getenv("DRAWINGS_FILEPATH", "./drawings.yaml")


def get_drawing_participants(draw_name):
    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)
    return configs.get('draws', {}).get(draw_name)


def draw(participants):
    not_drawn = [p for p in participants if not p.get("drawn")]
    not_already_played = [p for p in not_drawn if not p.get("offers_to")]

    # Special case: if only 2 people can be picked but one of them have not
    # played yet, we need to pick him otherwise he won't have anyone to pick
    if len(not_drawn) == 2 and len(not_already_played) == 1:
        return not_already_played[0]["name"]

    return random.choice(not_drawn)["name"]


def store_participation(draw_name, participant_name, offers_to_name):
    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)

    for person in configs['draws'][draw_name]:
        if person.get("name") == participant_name:
            person["offers_to"] = offers_to_name
        elif person.get("name") == offers_to_name:
            person["drawn"] = True

    with open(drawings_filepath, "w") as f:
        yaml.dump(configs, f)


def reset_draw(draw_name):
    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)

    for person in configs['draws'][draw_name]:
        person.pop("offers_to", None)
        person.pop("drawn", None)

    with open(drawings_filepath, "w") as f:
        yaml.dump(configs, f)


def can_reset(password):
    with open(drawings_filepath) as f:
        configs = yaml.safe_load(f)

    adminPass = configs.get('admin_password')

    return adminPass == password
