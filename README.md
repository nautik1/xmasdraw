
# xmasdraw

Flask app that just asks who you are, then draws another name
to whom you should offer a present.

## How to dev

```
pyenv version           # Displays version from .python-version
poetry env use python   # Select pyenv's local python
poetry install --with dev
poetry run flask --app "xmasdraw.app:app" run
```

## How to build & run

```
docker build -t nautik/xmasdraw .

docker run --restart unless-stopped -d -v $PWD/xmasdraw-data:/app/data -p 127.0.0.1:5000:5000 nautik/xmasdraw
```

## How to use

When first started, you need to generate the admin passphrase that you will use
to manage draws. Then, you can create/update/reset/delete any draw.

```
# Get your xkcd936 passphrase (admin password) and save it
http POST :5000/init language==fr

# Create your first draw
http :5000/draws X-Auth-Password:"<passphrase>" name=mydraw "participants[][name]=Hubert" "participants[][name]=Armand" "participants[][name]=Dolores" "participants[][name]=Fraulein"

# Start drawing
firefox http://localhost:5000/draws/mydraw
```

Note: you may be interested in setting a random name for your draw, so it is harder to discover on the internet (as there is no auth)

Other admin actions:
```
# Change the participants list (Note: will reset all participations)
http PUT :5000/draws/mydraw X-Auth-Password:"<passphrase>" "participants[][name]=toto" "participants[][name]=bibi" "participants[][name]=plarf"

# Reset participations (keeping participants)
http PURGE :5000/draws/mydraw X-Auth-Password:"<passphrase>"

# Delete a draw
http DELETE :5000/draws/mydraw X-Auth-Password:"<passphrase>"
```
