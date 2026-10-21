
# Blueprint organizes the book routes.
# request reads the client's submitted data.
# Book represents a book record.
# db lets you save records to the database.

from flask import Blueprint, Response, abort, make_response, request
from app.models.book import Book
from ..db import db
from app.route_utilities import validate_model

bp = Blueprint("books_bp", __name__, url_prefix="/books")


@bp.post("")
def create_book():
    request_body = request.get_json()

    try:
        new_book = Book.from_dict(request_body)

    except KeyError as error:
        response = {
            "message": f"Invalid request: missing {error.args[0]}"
        }
        abort(make_response(response, 400))

    db.session.add(new_book)
    db.session.commit()

    return new_book.to_dict(), 201


@bp.get("")
def get_all_books():
    query = db.select(Book)

    title_param = request.args.get("title")
    if title_param:
        query = query.where(
            Book.title.ilike(f"%{title_param}%")
        )

    description_param = request.args.get("description")
    if description_param:
        query = query.where(
            Book.description.ilike(f"%{description_param}%")
        )

    books = db.session.scalars(query.order_by(Book.id))

    books_response = []
    for book in books:
        books_response.append(book.to_dict())

    return books_response


@bp.get("/<book_id>")
def get_one_book(book_id):
    book = validate_book(Book, book_id)
    return book.to_dict()


def validate_book(cls, model_id):
    try:
        model_id = int(model_id)
    except ValueError:
        response = {
            "message": f"{cls.__name__} {model_id} invalid"
        }
        abort(make_response(response, 400))

    query = db.select(cls).where(cls.id == model_id)
    model = db.session.scalar(query)

    if not model:
        response = {
            "message": f"{cls.__name__} {model_id} not found"
        }
        abort(make_response(response, 404))

    return model


@bp.put("/<book_id>")
def update_book(book_id):
    book = validate_book(Book, book_id)
    request_body = request.get_json()

    book.title = request_body["title"]
    book.description = request_body["description"]
    db.session.commit()

    return Response(status=204, mimetype="application/json")


@bp.delete("/<book_id>")
def delete_book(book_id):
    book = validate_book(Book, book_id)
    db.session.delete(book)
    db.session.commit()

    return Response(status=204, mimetype="application/json")
