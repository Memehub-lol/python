from sqlalchemy import select
from src.generated.site_tables import ImgflipTemplates
from src.modules.template.template_repo import TemplateRepo


class TemplateService:
    repo = TemplateRepo

    @classmethod
    def get_train_names(cls, num_images: int) -> list[str]:
        with TemplateRepo.sessionmaker() as session:
            q = (select(ImgflipTemplates.name)
                 .where(ImgflipTemplates.num_images >= num_images)
                 .where(ImgflipTemplates.name == ImgflipTemplates.imgflip_name))
            return session.scalars(q).all()
