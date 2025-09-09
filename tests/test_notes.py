import pytest
import json
import sys
import os

# Add the parent directory to Python path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Note


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


def test_create_note_success(client):
    """Test successful note creation."""
    note_data = {
        "title": "Test Note",
        "body": "This is a test note body",
        "project": "test-project"
    }
    
    response = client.post('/api/notes', 
                          data=json.dumps(note_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Note created'
    assert 'id' in data
    
    # Verify note was actually created in database
    with client.application.app_context():
        note = Note.query.first()
        assert note.title == "Test Note"
        assert note.body == "This is a test note body"
        assert note.project == "test-project"


def test_create_note_validation_error_missing_title(client):
    """Test validation error when title is missing."""
    note_data = {
        "body": "This is a test note body",
        "project": "test-project"
    }
    
    response = client.post('/api/notes',
                          data=json.dumps(note_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid input'


def test_create_note_validation_error_missing_body(client):
    """Test validation error when body is missing."""
    note_data = {
        "title": "Test Note",
        "project": "test-project"
    }
    
    response = client.post('/api/notes',
                          data=json.dumps(note_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid input'


def test_create_note_validation_error_missing_project(client):
    """Test validation error when project is missing."""
    note_data = {
        "title": "Test Note",
        "body": "This is a test note body"
    }
    
    response = client.post('/api/notes',
                          data=json.dumps(note_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid input'


def test_create_note_validation_error_empty_data(client):
    """Test validation error when no data is provided."""
    response = client.post('/api/notes',
                          data=json.dumps({}),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['error'] == 'Invalid input'


def test_list_notes_empty(client):
    """Test listing notes when no notes exist."""
    response = client.get('/api/notes')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []


def test_list_notes_with_data(client):
    """Test listing notes when notes exist."""
    # Create a test note first
    with client.application.app_context():
        note = Note(title="Test Note", body="Test Body", project="test-project")
        db.session.add(note)
        db.session.commit()
    
    response = client.get('/api/notes')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == "Test Note"
    assert data[0]['body'] == "Test Body"
    assert data[0]['project'] == "test-project"


def test_list_notes_filter_by_project(client):
    """Test listing notes filtered by project."""
    # Create test notes
    with client.application.app_context():
        note1 = Note(title="Note 1", body="Body 1", project="project-a")
        note2 = Note(title="Note 2", body="Body 2", project="project-b")
        db.session.add(note1)
        db.session.add(note2)
        db.session.commit()
    
    response = client.get('/api/notes?project=project-a')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['project'] == "project-a"


def test_stats_endpoint(client):
    """Test the stats endpoint."""
    # Create a test note first
    with client.application.app_context():
        note = Note(title="Test Note", body="Test Body", project="test-project")
        db.session.add(note)
        db.session.commit()
    
    response = client.get('/api/stats')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total_notes'] == 1


def test_home_page(client):
    """Test the home page renders correctly."""
    response = client.get('/')
    
    assert response.status_code == 200
    assert b'<!doctype html>' in response.data
