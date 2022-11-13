from enum import Enum

from src.services.environment import Environment


class EDatabase(Enum):
    SITE = "SITE"
    TRAINING = "TRAINING"

    def get_config(self):
        if self is EDatabase.SITE:
            return Environment.get_site_db_connection_options()
        elif self is EDatabase.TRAINING:
            return Environment.get_training_db_connection_options()
        raise Exception("enum exhausted")

    def url(self):
        protocol, user, password, host, port, db_Name = self.get_config()
        return f"{protocol}://{user}:{password}@{host}:{port}/{db_Name}"
