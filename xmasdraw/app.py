from flask import Flask, render_template, request

from . import helpers, auth

app = Flask(__name__)


@app.route("/init", methods=["POST"])
@auth.check_init_status(need_init_done=False)
def init():
    passphrase = auth.generate_passphrase()
    return f'Store this passphrase: "{passphrase}". It will not be retrievable!'


@app.route("/")
@auth.check_init_status(need_init_done=True)
def home():
    return "You need to go to a draw URL."


@app.route("/draws/<draw_name>")
@auth.check_init_status(need_init_done=True)
def show_draw(draw_name):
    participants = helpers.get_drawing_participants(draw_name)

    if not participants:
        return "Tirage non trouve"

    return render_template("draw.html", draw_name=draw_name, participants=participants)


@app.route("/draws/<draw_name>/participants/<participant_name>", methods=["POST"])
@auth.check_init_status(need_init_done=True)
def participate(draw_name, participant_name):
    participants = helpers.get_drawing_participants(draw_name)

    if not participants:
        return "Tirage non trouve"

    participant = [
        p
        for p in participants
        if p["name"] == participant_name and p.get("offers_to") is None
    ]

    if len(participant) != 1:
        return "Participant non trouve"

    offers_to_name = helpers.draw(participants, participant_name)

    helpers.store_participation(draw_name, participant_name, offers_to_name)

    return render_template(
        "drawn.html",
        draw_name=draw_name,
        participant=participant_name,
        offers_to=offers_to_name,
    )


@app.route("/draws/<draw_name>", methods=["DELETE"])
@auth.check_init_status(need_init_done=True)
def reset(draw_name):
    password = request.headers.get("X-Auth-Password", None)
    if not password or not auth.verify_passphrase(password):
        return "You cannot reset this draw."

    helpers.reset_draw(draw_name)
    return "Reset done."


if __name__ == "__main__":
    app.run()
