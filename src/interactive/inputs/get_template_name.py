from sqlalchemy import select
from src.generated.site_tables import ImgflipTemplates
from src.interactive.inputs.input_handler import options_input_handler
from src.services.database import site_session_maker


def get_template_name():
    with site_session_maker() as session:
        offset = 0
        limit = 10
        while True:
            template_names = session.execute(select(ImgflipTemplates.name).offset(offset).limit(limit)).scalars().all()
            template_name = options_input_handler("Select Template:", template_names)
            if template_name is not None:
                return template_name
            offset += limit
