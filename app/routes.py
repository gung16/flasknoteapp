from flask import Blueprint, request, jsonify, render_template
from .extensions import db, cache, limiter
from .models import Note

notes_bp = Blueprint("notes", __name__)

# Home page - list notes
@notes_bp.route("/")
def index():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template("index.html", notes=notes)

# Create note (rate limited)
@notes_bp.route("/api/notes", methods=["POST"])
@limiter.limit("5/minute")
def add_note():
    data = request.get_json()
    if not data or not data.get("title") or not data.get("body") or not data.get("project"):
        return jsonify({"error": "Invalid input"}), 400

    note = Note(title=data["title"], body=data["body"], project=data["project"])
    db.session.add(note)
    db.session.commit()
    return jsonify({"message": "Note created", "id": note.id}), 201

# List notes
@notes_bp.route("/api/notes", methods=["GET"])
def list_notes():
    project = request.args.get("project")
    if project:
        notes = Note.query.filter_by(project=project).all()
    else:
        notes = Note.query.all()
    return jsonify([{"id": n.id, "title": n.title, "body": n.body,
                     "project": n.project, "created_at": n.created_at.isoformat()} for n in notes])

# Stats (cached)
@notes_bp.route("/api/stats")
@cache.cached()
def stats():
    count = Note.query.count()
    return jsonify({"total_notes": count})
