from core.Commons import add_into_db
from models import Language


def get_language_id(language, db_connect):
    search_result = (
        db_connect.query(Language).filter(Language.language == language).first()
    )
    return None if search_result is None else search_result.id


def add_language_to_db(language, db_connect):
    data = Language(language=language)
    add_into_db(data, db_connect)
    return data.id
