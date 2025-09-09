# Flask Notes App

A simple internal notes system built with Flask.

## Setup
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

export FLASK_APP=wsgi.py
flask db init
flask db migrate -m "init"
flask db upgrade

flask run

## Run in production:
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app

## Features
Add notes: POST /api/notes (title, body, project).

List notes: GET /api/notes, filter by ?project=.

Simple HTML at /.

Stats: GET /api/stats (cached).

Validation: invalid input returns 400.

Rate limiting: 5 notes/min per client.

Custom header: X-Request-ID on every response.

## Key Concepts
Routes: Flask maps URLs to Python functions with @app.route or blueprint routes.

flask.request: Provides request data like request.get_json() (body) and request.args (query params).

Blueprints & Factory: Blueprints organize routes into modules; the factory (create_app) builds the app cleanly for config and testing.

Extensions: Add functionality:
- Flask-SQLAlchemy → database ORM
- Flask-Migrate → schema changes
- Flask-Caching → caching
- Flask-Limiter → rate limits
- Custom after_request → adds X-Request-ID

Gunicorn: A WSGI server that runs Flask with multiple workers in production, e.g. gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app.