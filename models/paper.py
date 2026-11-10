
from extensions import db
from datetime import datetime


class Paper(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(500), nullable=False)

    authors = db.Column(db.Text)

    abstract = db.Column(db.Text)

    publication_year = db.Column(db.Integer)

    journal = db.Column(db.String(300))

    doi = db.Column(db.String(300), unique=True)

    source = db.Column(db.String(100))

    external_id = db.Column(db.String(300))

    paper_url = db.Column(db.String(1000))

    pdf_path = db.Column(db.String(500))

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
