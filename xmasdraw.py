from flask import Flask, render_template, request
import helpers

app = Flask(__name__)


@app.route("/")
def home():
    return "You need to go to a draw URL."


@app.route("/<draw_name>/draw")
def show_draw(draw_name):
    participants = helpers.get_drawing_participants(draw_name)

    if not participants:
        return "Tirage non trouve"

    return render_template("draw.html", draw_name=draw_name, participants=participants)


@app.route("/<draw_name>/draw/<participant_name>", methods=["POST"])
def participate(draw_name, participant_name):
    remaining_participants = helpers.get_drawing_participants(draw_name)

    if not remaining_participants:
        return "Tirage non trouve"

    participant = [
        remaining_participants.pop(idx)
        for idx, value in enumerate(remaining_participants)
        if value.get("name") == participant_name
    ]

    if len(participant) != 1:
        return "Participant non trouve"

    offers_to = helpers.draw(remaining_participants)

    participant = participant[0]
    helpers.store_participation(draw_name, participant, offers_to)

    return render_template(
        "drawn.html",
        draw_name=draw_name,
        participant=participant,
        offers_to=offers_to,
    )


@app.route("/<draw_name>/draw", methods=["DELETE"])
def reset(draw_name):
    user = request.headers.get("user", None)
    if not user or not helpers.can_reset(draw_name, user):
        return "You cannot reset this draw."

    helpers.reset_draw(draw_name)
    return "Reset done."


if __name__ == "__main__":
    app.run()
