from .base import BaseRepository
# removed circular import; db and QuickNotes passed in

class QuickNotesRepository(BaseRepository):
    def __init__(self, db, QuickNotes):
        super().__init__(db, QuickNotes)

    def get_or_create(self):
        notes = self.model.query.first()
        if notes is None:
            notes = self.model(content="")
            self.add(notes)
        return notes
