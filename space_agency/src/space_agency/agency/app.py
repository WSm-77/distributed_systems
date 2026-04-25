
import argparse
from space_agency.agency.agency import Agency
from space_agency.utils.utils import create_logger
from space_agency.shared.models import Services

logger = create_logger(__name__)

def help():
    logger.info("Usage: agency --name <name>")
    logger.info("Available services:")
    for service in Services:
        logger.info(f"- {service.value}")

def app():
    parser = argparse.ArgumentParser(description="Agency service")
    parser.add_argument("--name", type=str, required=True, help="Name of the agency")
    args = parser.parse_args()
    agency = Agency(
        name=args.name,
    )
    agency.run()

if __name__ == "__main__":
    app()
