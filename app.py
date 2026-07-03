import os
import re
from datetime import date, datetime, timezone

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todos.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

todo_categories = db.Table(
    "todo_categories",
    db.Column("todo_id", db.Integer, db.ForeignKey("todo.id"), primary_key=True),
    db.Column("category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True),
)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    todos = db.relationship("Todo", secondary=todo_categories, back_populates="categories")

    @property
    def display_name(self):
        return self.name.replace("-", " ").title()


class QuickNotes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, default="")
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    categories = db.relationship("Category", secondary=todo_categories, back_populates="todos")

    @property
    def created_at_local(self):
        return self.created_at.replace(tzinfo=timezone.utc).astimezone()

    @property
    def is_overdue(self):
        if self.completed or not self.due_date:
            return False
        return self.due_date < date.today()

    @property
    def is_due_today(self):
        if self.completed or not self.due_date:
            return False
        return self.due_date == date.today()


def migrate_db():
    db.create_all()
    inspector = inspect(db.engine)
    if inspector.has_table("todo"):
        columns = {column["name"] for column in inspector.get_columns("todo")}
        if "due_date" not in columns:
            with db.engine.begin() as connection:
                connection.execute(text("ALTER TABLE todo ADD COLUMN due_date DATE"))


def parse_tag_names(raw_tags):
    if not raw_tags:
        return []
    parts = re.split(r"[,\n]+", raw_tags)
    seen = set()
    tags = []
    for part in parts:
        normalized = part.strip().lower()
        if normalized and normalized not in seen:
            seen.add(normalized)
            tags.append(normalized)
    return tags


def sync_todo_categories(todo, raw_tags):
    tag_names = parse_tag_names(raw_tags)
    categories = []
    for name in tag_names:
        category = Category.query.filter_by(name=name).first()
        if category is None:
            category = Category(name=name)
            db.session.add(category)
        categories.append(category)
    todo.categories = categories


def parse_due_date(raw_due_date):
    if not raw_due_date:
        return None
    try:
        return date.fromisoformat(raw_due_date)
    except ValueError:
        return None


def get_selected_category_ids():
    selected = []
    for value in request.args.getlist("categories"):
        if value.isdigit():
            selected.append(int(value))
    return selected


def get_quick_notes():
    notes = QuickNotes.query.first()
    if notes is None:
        notes = QuickNotes(content="")
        db.session.add(notes)
        db.session.commit()
    return notes


def form_context(todo=None, title="", description="", due_date="", tags=""):
    return {
        "todo": todo,
        "title": title,
        "description": description,
        "due_date": due_date,
        "tags": tags,
        "all_categories": Category.query.order_by(Category.name).all(),
    }


with app.app_context():
    migrate_db()


@app.route("/")
def index():
    filter_status = request.args.get("filter", "all")
    selected_category_ids = get_selected_category_ids()
    query = Todo.query.order_by(Todo.created_at.desc())

    if filter_status == "active":
        query = query.filter_by(completed=False)
    elif filter_status == "completed":
        query = query.filter_by(completed=True)

    if selected_category_ids:
        query = query.filter(Todo.categories.any(Category.id.in_(selected_category_ids)))

    todos = query.all()
    all_categories = Category.query.order_by(Category.name).all()

    quick_notes = get_quick_notes()

    return render_template(
        "index.html",
        todos=todos,
        filter_status=filter_status,
        all_categories=all_categories,
        selected_category_ids=selected_category_ids,
        quick_notes=quick_notes,
    )


@app.route("/api/quick-notes", methods=["GET", "POST"])
def quick_notes_api():
    notes = get_quick_notes()

    if request.method == "POST":
        payload = request.get_json(silent=True) or {}
        notes.content = payload.get("content", "")
        notes.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"ok": True})

    return jsonify({"content": notes.content or ""})


@app.route("/todos/new", methods=["GET", "POST"])
def create_todo():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "")
        due_date = parse_due_date(request.form.get("due_date", ""))
        tags = request.form.get("tags", "")

        if not title:
            flash("Title is required.", "danger")
            return render_template(
                "form.html",
                **form_context(title=title, description=description, due_date=request.form.get("due_date", ""), tags=tags),
            )

        todo = Todo(title=title, description=description, due_date=due_date)
        db.session.add(todo)
        sync_todo_categories(todo, tags)
        db.session.commit()
        flash("Todo created.", "success")
        return redirect(url_for("index"))

    return render_template("form.html", **form_context())


@app.route("/todos/<int:todo_id>/edit", methods=["GET", "POST"])
def edit_todo(todo_id):
    todo = db.get_or_404(Todo, todo_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "")
        due_date = parse_due_date(request.form.get("due_date", ""))
        tags = request.form.get("tags", "")

        if not title:
            flash("Title is required.", "danger")
            return render_template(
                "form.html",
                **form_context(
                    todo=todo,
                    title=title,
                    description=description,
                    due_date=request.form.get("due_date", ""),
                    tags=tags,
                ),
            )

        todo.title = title
        todo.description = description
        todo.due_date = due_date
        sync_todo_categories(todo, tags)
        db.session.commit()
        flash("Todo updated.", "success")
        return redirect(url_for("index"))

    tags = ", ".join(category.display_name for category in sorted(todo.categories, key=lambda c: c.name))
    due_date = todo.due_date.isoformat() if todo.due_date else ""

    return render_template(
        "form.html",
        **form_context(todo=todo, title=todo.title, description=todo.description, due_date=due_date, tags=tags),
    )


@app.route("/todos/<int:todo_id>/toggle", methods=["POST"])
def toggle_todo(todo_id):
    todo = db.get_or_404(Todo, todo_id)
    todo.completed = not todo.completed
    db.session.commit()
    flash("Todo marked as {}.".format("completed" if todo.completed else "active"), "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/todos/<int:todo_id>/delete", methods=["POST"])
def delete_todo(todo_id):
    todo = db.get_or_404(Todo, todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash("Todo deleted.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
