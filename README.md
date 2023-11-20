
# xmasdraw

Flask app that just asks who you are, then draws another name
to whom you should offer a present.

## How to dev

```
pyenv version           # Displays version from .python-version
poetry env use python   # Select pyenv's local python
poetry install
cp drawings.yaml.sample drawings.yaml
poetry run flask --app "xmasdraw.app:app" run
firefox http://localhost:5000/draws/myfamily
```

## How to build & run

```
docker build -t nautik/xmasdraw .

mkdir data/
cp drawings.yaml.sample data/drawings.yaml

docker run --restart unless-stopped -d -v $PWD/xmasdraw:/app/data -p 127.0.0.1:5000:5000 nautik/xmasdraw
```
