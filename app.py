from flask import Flask, render_template
import helpers

app = Flask(__name__)


@app.route("/")
def home(path):
    return "You need to go to a draw URL."

@app.route("/<draw_name>/draw")
def draw(draw_name):
    participants = helpers.get_drawing_participants(draw_name)

    if not participants:
        return "Tirage non trouve"

    return render_template("draw.html", draw_name=draw_name, participants=participants)


if __name__ == "__main__":
    app.run()
