from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for
)
from flask_login import login_required, current_user
from extensions import db
from models.paper import Paper
import requests
from models.collection import Collection

research = Blueprint("research", __name__)

OPENALEX_API = "https://api.openalex.org/works"


def reconstruct_abstract(inverted_index):

    if not inverted_index:
        return ""

    words = {}

    for word, positions in inverted_index.items():
        for position in positions:
            words[position] = word

    return " ".join(
        words[position]
        for position in sorted(words)
    )


def normalize_paper(work):

    authors = []

    for authorship in work.get("authorships", []):
        author = authorship.get("author", {})
        name = author.get("display_name")

        if name:
            authors.append(name)

    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}

    best_location = work.get("best_oa_location") or {}

    doi = work.get("doi")

    return {
        "external_id": work.get("id"),
        "title": work.get("title") or "Untitled paper",
        "authors": authors,
        "abstract": reconstruct_abstract(
            work.get("abstract_inverted_index")
        ),
        "year": work.get("publication_year"),
        "journal": source.get("display_name"),
        "doi": doi,
        "paper_url": (
            best_location.get("landing_page_url")
            or doi
            or work.get("id")
        ),
        "pdf_url": best_location.get("pdf_url"),
        "is_open_access": (
            work.get("open_access") or {}
        ).get("is_oa", False)
    }


# Research Library page
@research.route("/research")
@login_required
def library():

    return render_template("research.html")


# Search scientific publications
@research.route("/api/research/search")
@login_required
def search_papers():

    query = request.args.get("q", "").strip()
    year = request.args.get("year", "").strip()
    open_access = request.args.get("open_access", "")

    if not query:
        return jsonify({
            "results": [],
            "error": "Enter a search term."
        }), 400

    if len(query) > 200:
        return jsonify({
            "results": [],
            "error": "Search term is too long."
        }), 400

    params = {
        "search": query,
        "per_page": 15,
        "sort": "relevance_score:desc",
        "select": (
            "id,doi,title,publication_year,authorships,"
            "abstract_inverted_index,primary_location,"
            "best_oa_location,open_access,type,cited_by_count"
        )
    }

    filters = []

    if year:
        try:
            year_value = int(year)

            if year_value < 1800 or year_value > 2100:
                raise ValueError

            filters.append(
                f"publication_year:{year_value}"
            )

        except ValueError:
            return jsonify({
                "results": [],
                "error": "Enter a valid publication year."
            }), 400

    if open_access == "true":
        filters.append("open_access.is_oa:true")

    if filters:
        params["filter"] = ",".join(filters)

    try:

        response = requests.get(
            OPENALEX_API,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        works = response.json().get("results", [])

        results = [
            normalize_paper(work)
            for work in works
        ]

        return jsonify({
            "results": results,
            "count": len(results)
        })

    except requests.RequestException:
        return jsonify({
            "results": [],
            "error": "Unable to connect to the research database."
        }), 503


# Save a paper to the user's library
@research.route("/api/research/save", methods=["POST"])
@login_required
def save_paper():

    data = request.get_json(silent=True) or {}

    external_id = data.get("external_id")
    doi = data.get("doi")
    title = data.get("title")

    if not external_id or not title:
        return jsonify({
            "error": "Paper information is incomplete."
        }), 400

    if not isinstance(title, str) or len(title) > 500:
        return jsonify({
            "error": "Invalid paper title."
        }), 400

    paper = Paper.query.filter_by(
        external_id=external_id
    ).first()

    if not paper and doi:
        paper = Paper.query.filter_by(
            doi=doi
        ).first()

    if not paper:

        authors = data.get("authors", [])

        paper = Paper(
            title=title,
            authors=", ".join(authors),
            abstract=data.get("abstract", ""),
            publication_year=data.get("year"),
            journal=data.get("journal"),
            doi=doi,
            source="OpenAlex",
            external_id=external_id,
            paper_url=data.get("paper_url")
        )

        db.session.add(paper)
        db.session.flush()

    if paper not in current_user.saved_papers:
        current_user.saved_papers.append(paper)

    db.session.commit()

    return jsonify({
        "message": "Paper saved successfully."
    })


# View saved papers
@research.route("/my-research")
@login_required
def my_research():

    papers = current_user.saved_papers
    collections = current_user.collections.all()

    return render_template(
        "my_research.html",
        papers=papers,
        collections=collections
    )

# Remove a saved paper
@research.route(
    "/api/research/unsave/<int:paper_id>",
    methods=["POST"]
)
@login_required
def unsave_paper(paper_id):

    paper = Paper.query.get_or_404(paper_id)

    if paper in current_user.saved_papers:
        current_user.saved_papers.remove(paper)
        db.session.commit()

    return jsonify({
        "message": "Paper removed from your library."
    })
# Add a saved paper to a collection
@research.route(
    "/collections/add-paper",
    methods=["POST"]
)
@login_required
def add_to_collection():

    paper_id = request.form.get("paper_id", type=int)
    collection_id = request.form.get("collection_id", type=int)

    paper = Paper.query.get_or_404(paper_id)

    # Make sure the paper belongs to the user's library
    if paper not in current_user.saved_papers:
        flash("This paper is not in your research library.", "error")
        return redirect(url_for("research.my_research"))

    # Make sure the collection belongs to the logged-in user
    collection = Collection.query.filter_by(
        id=collection_id,
        user_id=current_user.id
    ).first_or_404()

    if paper not in collection.papers:
        collection.papers.append(paper)
        db.session.commit()
        flash("Paper added to collection!", "success")
    else:
        flash("This paper is already in that collection.", "error")

    return redirect(url_for("research.my_research"))