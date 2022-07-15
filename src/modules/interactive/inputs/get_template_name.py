from src.lib.services.database import site_session_maker
from src.modules.generated.site_tables import Templates
from src.modules.interactive.inputs.input_handler import options_input_handler
from sqlalchemy import select


def get_template_name():
    with site_session_maker() as session:
        offset = 0
        limit = 10
        while True:
            template_names = session.execute(select(Templates.name).offset(offset).limit(limit)).scalars().all()
            template_name = options_input_handler("Select Template:", template_names, nullable=True)
            if template_name is not None:
                return template_name
            offset += limit
