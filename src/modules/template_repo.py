

from sqlalchemy import func, select

from src.generated.site_tables import ImgflipTemplates
from src.services.database import site_session_maker


class TemplateRepo:

    @classmethod
    def count(cls) -> int:
        with site_session_maker() as session:
            return session.scalar(select(func.count(ImgflipTemplates.name.distinct())))
        
    @classmethod
    def get_train_names(cls, num_images: int) -> list[str]:
        with site_session_maker() as session:
            q = (select(ImgflipTemplates.name)
                 .where(ImgflipTemplates.num_images >= num_images)
                 .where(ImgflipTemplates.name == ImgflipTemplates.imgflip_name))
            return session.scalars(q).all()
