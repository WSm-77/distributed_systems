import argparse
from space_agency.carrier.carrier import Carrier
from space_agency.utils.utils import create_logger
from space_agency.shared.models import Services

logger = create_logger(__name__)

def help():
    logger.info("Usage: carrier --name <name> --first-service <service> --second-service <service>")
    logger.info("Available services:")
    for service in Services:
        logger.info(f"- {service.value}")

def app():
    parser = argparse.ArgumentParser(description="Carrier service")
    parser.add_argument("--name", type=str, required=True, help="Name of the carrier")
    parser.add_argument("--first-service", type=Services, required=True, help="First service provided by the carrier")
    parser.add_argument("--second-service", type=Services, required=True, help="Second service provided by the carrier")
    args = parser.parse_args()
    carrier = Carrier(
        name=args.name,
        first_service=args.first_service,
        second_service=args.second_service
    )
    carrier.run()

if __name__ == "__main__":
    app()
