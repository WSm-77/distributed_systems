from space_agency.shared.models import Services
from space_agency.utils.utils import create_logger

logger = create_logger(__name__)

class Carrier:
    def __init__(self, name: str, first_service: Services, second_service: Services):
        self.name = name
        self.first_service = first_service
        self.second_service = second_service

    def run(self):
        logger.info(f"Carrier {self.name} is running.")
        logger.info(f"First service: {self.first_service.value}")
        logger.info(f"Second service: {self.second_service.value}")
