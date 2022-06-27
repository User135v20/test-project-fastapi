from sqlalchemy.orm import Session
from core.Commons import add_into_db
from models import Language


def get_language_id(language, db: Session):
    search_result = db.query(Language).filter(Language.language == language).first()
    return None if search_result is None else search_result.id


def add_language_to_db(language, db):
    data = Language(language=language)
    add_into_db(data, db)
    return data.id