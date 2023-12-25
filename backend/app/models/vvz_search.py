from beanie import Document, before_event, Replace, Insert
from datetime import datetime
from pydantic import Field

from backend.app.schemas.vvz_search import Result


class VvzSearchResult(Result, Document):
    les: str = "Ves"

    update_at: datetime = Field(default_factory=datetime.utcnow)
    
    
    @before_event(Replace, Insert)
    def update_updated_at(self):
        self.update_at = datetime.utcnow()



    
    class Settings:
        name = "results"