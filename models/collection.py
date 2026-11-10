from extensions import db
from datetime import datetime


# Connects users to papers saved in their personal library
saved_papers = db.Table(
    "saved_papers",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("paper_id", db.Integer, db.ForeignKey("paper.id"), primary_key=True),
    db.Column("saved_at", db.DateTime, default=datetime.utcnow)
)


# Connects collections to the papers inside them
collection_papers = db.Table(
    "collection_papers",
    db.Column("collection_id", db.Integer, db.ForeignKey("collection.id"), primary_key=True),
    db.Column("paper_id", db.Integer, db.ForeignKey("paper.id"), primary_key=True)
)


class Collection(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(150), nullable=False)

    description = db.Column(db.Text)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    papers = db.relationship(
        "Paper",
        secondary=collection_papers,
        backref="collections"
    )