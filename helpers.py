import yaml

DRAWINGS_FILEPATH = "drawings.yaml"


def get_drawing_participants(draw_name):

    with open(DRAWINGS_FILEPATH) as f:
        drawings = yaml.safe_load(f)

    return drawings.get(draw_name)
