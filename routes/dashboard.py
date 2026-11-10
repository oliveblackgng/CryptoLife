
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from extensions import db
from models.collection import Collection

dashboard = Blueprint("dashboard", __name__)


# Dashboard
@dashboard.route("/dashboard")
@login_required
def home():

    saved_count = len(current_user.saved_papers)
    collection_count = current_user.collections.count()

    return render_template(
        "dashboard.html",
        saved_count=saved_count,
        collection_count=collection_count
    )


# View collections
@dashboard.route("/collections")
@login_required
def collections():

    user_collections = current_user.collections.all()

    return render_template(
        "collections.html",
        collections=user_collections
    )


# Create a collection
@dashboard.route("/collections/create", methods=["POST"])
@login_required
def create_collection():

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        flash("Please enter a collection name.", "error")
        return redirect(url_for("dashboard.collections"))

    if len(name) > 150:
        flash("Collection name is too long.", "error")
        return redirect(url_for("dashboard.collections"))

    collection = Collection(
        name=name,
        description=description,
        user_id=current_user.id
    )

    db.session.add(collection)
    db.session.commit()

    flash("Collection created successfully!", "success")

    return redirect(url_for("dashboard.collections"))
@dashboard.route("/collections/<int:collection_id>")
@login_required
def view_collection(collection_id):

    collection = Collection.query.filter_by(
        id=collection_id,
        user_id=current_user.id
    ).first_or_404()

    return render_template(
        "collection_detail.html",
        collection=collection,
        papers=collection.papers
    )
