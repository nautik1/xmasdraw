from functools import wraps
from pathlib import Path

from flask import Flask, render_template, request
from marshmallow import Schema, ValidationError, fields, validate

from . import auth, helpers

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


class UpdateDrawRequestSchema(Schema):
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


def check_admin_authentication():
    def _check_admin_authentication(func):
        @wraps(func)
        def __check_admin_authentication(*args, **kwargs):
            password = request.headers.get("X-Auth-Password", None)
            if not password or not auth.verify_passphrase(password):
                return "Not authorized.", 403
            return func(*args, **kwargs)

        return __check_admin_authentication

    return _check_admin_authentication


################
# Admin routes #
################


@app.route("/init", methods=["POST"])
def init():
    if auth.is_admin_password_set():
        return "Too late, init already done", 422

    requested_language = request.args.get("language")
    supported_languages = ["fr", "en"]
    if (
        requested_language is not None
        and requested_language.lower() not in supported_languages
    ):
        return f"Unsupported language; only {supported_languages} allowed", 422

    # Create the file if it does not exist
    Path(helpers.drawings_filepath).touch(exist_ok=True)

    passphrase = auth.generate_passphrase(requested_language)
    return f'Store this passphrase: "{passphrase}". It will not be retrievable again!'


@app.route("/draws", methods=["POST"])
@check_init_is_done()
@check_admin_authentication()
def create_draw():
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


@app.route("/draws/<draw_name>", methods=["PUT"])
@check_init_is_done()
@check_admin_authentication()
def update_draw_participants(draw_name):
    requestSchema = UpdateDrawRequestSchema()
    try:
        params = requestSchema.load(request.json)
    except ValidationError as err:
        return str(err), 422

    try:
        helpers.update_draw(draw_name, params["participants"])
    except helpers.DrawException as err:
        return str(err), 422

    return "Updated!"


@app.route("/draws/<draw_name>", methods=["PURGE", "DELETE"])
@check_init_is_done()
@check_admin_authentication()
def administrate_draw(draw_name):
    handler = {
        "PURGE": helpers.reset_draw,
        "DELETE": helpers.delete_draw,
    }[request.method]

    try:
        handler(draw_name)
    except helpers.DrawException as err:
        return str(err), 422

    return "Done!"


######################
# Participant routes #
######################


@app.route("/")
@check_init_is_done()
def home():
    return "You need to go to a draw URL."


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


if __name__ == "__main__":
    app.run()
