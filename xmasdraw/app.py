from flask import Flask, render_template, request

from . import helpers

app = Flask(__name__)


@app.route("/")
def home():
    return "You need to go to a draw URL."


@app.route("/draws/<draw_name>")
def show_draw(draw_name):
    participants = helpers.get_drawing_participants(draw_name)

    if not participants:
        return "Tirage non trouve"

    return render_template("draw.html", draw_name=draw_name, participants=participants)


@app.route("/draws/<draw_name>/participants/<participant_name>", methods=["POST"])
def participate(draw_name, participant_name):
    remaining_participants = helpers.get_drawing_participants(draw_name)

    if not remaining_participants:
        return "Tirage non trouve"

    participant = [
        remaining_participants.pop(idx)
        for idx, value in enumerate(remaining_participants)
        if value["name"] == participant_name
    ]

    if len(participant) != 1:
        return "Participant non trouve"

    participant = participant[0]
    offers_to_name = participant.get("offers_to", None)
    if not offers_to_name:
        offers_to_name = helpers.draw(remaining_participants)

    helpers.store_participation(draw_name, participant["name"], offers_to_name)

    return render_template(
        "drawn.html",
        draw_name=draw_name,
        participant=participant["name"],
        offers_to=offers_to_name,
    )


@app.route("/draws/<draw_name>", methods=["DELETE"])
def reset(draw_name):
    username = request.headers.get("User", None)
    password = request.headers.get("Password", None)
    if not password or not helpers.can_reset(draw_name, username, password):
        return "You cannot reset this draw."

    helpers.reset_draw(draw_name)
    return "Reset done."


if __name__ == "__main__":
    app.run()
