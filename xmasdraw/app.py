from flask import Flask, render_template, request
from marshmallow import Schema, fields, ValidationError, validate
from pathlib import Path

from functools import wraps
from . import helpers, auth

app = Flask(__name__)

###########
# Schemas #
###########


class ParticipantSchema(Schema):
    name = fields.String(required=True)


class CreateDrawRequestSchema(Schema):
    name = fields.String(required=True)
    participants = fields.List(
        fields.Nested(ParticipantSchema), required=True, validate=validate.Length(2)
    )


##############
# Validators #
##############


def check_init_is_done():
    def _check_init_is_done(func):
        @wraps(func)
        def __check_init_is_done(*args, **kwargs):
            if not auth.is_admin_password_set():
                return "Need to init the instance first", 422
            return func(*args, **kwargs)

        return __check_init_is_done

    return _check_init_is_done


##########
# Routes #
##########


@app.route("/init", methods=["POST"])
def init():
    if auth.is_admin_password_set():
        return "Too late, init already done", 422

    # Create the file if it does not exist
    Path(helpers.drawings_filepath).touch(exist_ok=True)

    passphrase = auth.generate_passphrase()
    return f'Store this passphrase: "{passphrase}". It will not be retrievable again!'


@app.route("/")
@check_init_is_done()
def home():
    return "You need to go to a draw URL."


@app.route("/draws", methods=["POST"])
@check_init_is_done()
def create_draw():
    password = request.headers.get("X-Auth-Password", None)
    if not password or not auth.verify_passphrase(password):
        return "You cannot create a draw.", 403

    requestSchema = CreateDrawRequestSchema()
    try:
        params = requestSchema.load(request.json)
    except ValidationError as err:
        return str(err), 422

    try:
        helpers.create_draw(params)
    except helpers.DrawException as err:
        return str(err), 422

    return "Created!"


@app.route("/draws/<draw_name>")
@check_init_is_done()
def show_draw(draw_name):
    participants = helpers.get_drawing_participants(draw_name)

    if not participants:
        return "Tirage non trouve", 400

    return render_template("draw.html", draw_name=draw_name, participants=participants)


@app.route("/draws/<draw_name>/participants/<participant_name>", methods=["POST"])
@check_init_is_done()
def participate(draw_name, participant_name):
    participants = helpers.get_drawing_participants(draw_name)

    if not participants:
        return "Tirage non trouve", 400

    participant = [
        p
        for p in participants
        if p["name"] == participant_name and p.get("offers_to") is None
    ]

    if len(participant) != 1:
        return "Participant non trouve", 400

    try:
        offers_to_name = helpers.draw(participants, participant_name)
    except helpers.DrawException as err:
        return str(err), 422

    helpers.store_participation(draw_name, participant_name, offers_to_name)

    return render_template(
        "drawn.html",
        draw_name=draw_name,
        participant=participant_name,
        offers_to=offers_to_name,
    )


@app.route("/draws/<draw_name>", methods=["DELETE"])
@check_init_is_done()
def reset(draw_name):
    password = request.headers.get("X-Auth-Password", None)
    if not password or not auth.verify_passphrase(password):
        return "You cannot reset this draw.", 403

    helpers.reset_draw(draw_name)
    return "Reset done."


if __name__ == "__main__":
    app.run()
