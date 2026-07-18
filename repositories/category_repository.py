from .base import BaseRepository
import re

class CategoryRepository(BaseRepository):
    def __init__(self, db, Category, Todo):
        super().__init__(db, Category)
        self.Todo = Todo

    def find_by_name(self, name):
        key = name.lower()
        return self.model.query.filter(self.db.func.lower(self.model.name) == key).first()

    def sync_categories(self, todo, raw_tags):
        if not raw_tags:
            return
        parts = re.split(r"[, ]+", raw_tags)
        seen = set()
        tags = []
        for part in parts:
            name = part.strip()
            key = name.lower()
            if name and key not in seen:
                seen.add(key)
                tags.append(name)
        categories = []
        for name in tags:
            category = self.find_by_name(name)
            if category is None:
                category = self.model(name=name)
                self.db.session.add(category)
            elif category.name != name:
                category.name = name
            categories.append(category)
        todo.categories = categories

    def get_available(self, filter_status="all", include_ids=None):
        include_ids = list(include_ids or [])
        query = self.model.query
        if filter_status == "active":
            query = query.filter(self.model.todos.any(self.Todo.completed.is_(False)))
        elif filter_status == "completed":
            query = query.filter(self.model.todos.any(self.Todo.completed.is_(True)))
        else:
            query = query.filter(self.model.todos.any())
        categories = {c.id: c for c in query.order_by(self.model.name).all()}
        if include_ids:
            for c in self.model.query.filter(self.model.id.in_(include_ids)).all():
                categories[c.id] = c
        return sorted(categories.values(), key=lambda c: c.name)
