from datetime import datetime

from pydantic import Field

from backend.app.schemas.vvz import SearchResultSchema
from beanie import Document, Insert, Replace, before_event


class SearchResult(SearchResultSchema, Document):
    update_at: datetime = Field(default_factory=datetime.utcnow)
    processed: bool = Field(default=False)

    @before_event(Replace, Insert)
    def update_updated_at(self):
        self.update_at = datetime.utcnow()

    class Settings:
        name = "Result"
