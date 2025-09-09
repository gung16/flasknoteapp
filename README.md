# Flask Notes App

A simple internal notes system built with Flask that demonstrates key Flask concepts and patterns.

## Setup

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

export FLASK_APP=wsgi.py
flask db init
flask db migrate -m "init"
flask db upgrade

flask run
```

## Run in production:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app
```

## Features
- Add notes: POST /api/notes (title, body, project)
- List notes: GET /api/notes, filter by ?project=
- Simple HTML at /
- Stats: GET /api/stats (cached)
- Validation: invalid input returns 400
- Rate limiting: 5 notes/min per client
- Custom header: X-Request-ID on every response

## Key Flask Concepts Explained

### How Flask Handles Routes

Flask uses a simple but powerful routing system that maps URLs to Python functions. When you use the `@app.route()` decorator, you're telling Flask "when someone visits this URL, run this function." 

In this app, we have routes like:
- `@notes_bp.route("/")` - maps the home page to the `index()` function
- `@notes_bp.route("/api/notes", methods=["POST"])` - maps POST requests to `/api/notes` to the `add_note()` function

Flask automatically handles the HTTP method matching, so GET requests to `/api/notes` go to `list_notes()` while POST requests go to `add_note()`. The routing system is what makes Flask so intuitive - you just write a function and tell Flask which URL should trigger it.

### How flask.request Works

The `flask.request` object is Flask's way of giving you access to all the data that came with the HTTP request. Think of it as a window into what the client sent you.

Key methods I use in this app:
- `request.get_json()` - extracts JSON data from the request body (like when creating a note)
- `request.args.get("project")` - gets query parameters from the URL (like `?project=myproject`)

For example, when someone POSTs to `/api/notes` with JSON data, `request.get_json()` gives me a Python dictionary I can work with. When they GET `/api/notes?project=work`, `request.args.get("project")` returns "work". This makes it easy to handle different types of client input without worrying about the low-level HTTP details.

### Why Blueprints and the Factory Pattern Matter

**Blueprints** are Flask's way of organizing your code into modules. Instead of putting all your routes in one big file, you can group related routes together. In this app, I created a `notes_bp` blueprint that contains all the note-related routes. This makes the code more maintainable - if I want to add user authentication later, I can create a separate `auth_bp` blueprint without cluttering the notes code.

**The Factory Pattern** (the `create_app()` function) is crucial for flexibility and testing. Instead of creating the Flask app at module level, I create it inside a function. This means I can:
- Create different app instances with different configurations (development vs production)
- Easily test the app by creating a test instance with test database
- Import the app creation function without automatically creating the app

This pattern separates "how to build the app" from "what the app does," making it much easier to manage different environments and write tests.

### How Extensions Work

Flask extensions add functionality to your app without you having to write everything from scratch. They follow a consistent pattern: create an extension object, initialize it with your app, then use it.

In this app, I use several extensions:

**Flask-SQLAlchemy** - Adds database ORM capabilities:
```python
db = SQLAlchemy()  # Create the extension
db.init_app(app)   # Initialize with app
# Then use: db.session.add(note), Note.query.all()
```

**Flask-Migrate** - Handles database schema changes:
```python
migrate = Migrate()
migrate.init_app(app, db)
# Enables: flask db migrate, flask db upgrade
```

**Flask-Caching** - Adds caching capabilities:
```python
cache = Cache()
cache.init_app(app)
# Use with: @cache.cached() decorator
```

**Flask-Limiter** - Adds rate limiting:
```python
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)
# Use with: @limiter.limit("5/minute")
```

**Custom Extension** - I also created a custom extension using Flask's `after_request` hook:
```python
@app.after_request
def add_request_id(response):
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    return response
```

This adds a unique request ID to every response, which is useful for debugging and tracking requests across distributed systems.

### How Gunicorn Integrates with Flask

Gunicorn is a WSGI (Web Server Gateway Interface) server that acts as a bridge between your Flask app and the web. Flask's built-in development server is great for testing, but it's not suitable for production because it can't handle multiple requests efficiently.

Gunicorn solves this by:
- **Running multiple worker processes** - The `-w 4` flag creates 4 worker processes, so your app can handle 4 requests simultaneously
- **Managing the WSGI interface** - It translates HTTP requests into the format Flask expects and converts Flask responses back to HTTP
- **Handling production concerns** - Process management, logging, graceful restarts, etc.

When you run `gunicorn -w 4 -b 0.0.0.0:8000 wsgi:app`, Gunicorn:
1. Imports the `app` object from `wsgi.py`
2. Creates 4 worker processes
3. Binds to all interfaces (`0.0.0.0`) on port 8000
4. Each worker runs your Flask app and can handle requests independently

This setup can handle much more traffic than Flask's development server and is what you'd use in a real production environment.

## Testing

Run the tests with:
```bash
pytest tests/
```

The test suite includes:
- Note creation success scenarios
- Validation error handling (missing fields)
- Note listing and filtering
- Stats endpoint functionality
- Home page rendering