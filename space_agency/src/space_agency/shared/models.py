from enum import Enum

class Services(str, Enum):
    PEOPLE_TRANSPORT = "people_transport"
    CARGO_TRANSPORT = "cargo_transport"
    SATELLITE_DEPLOYMENT = "satellite_deployment"

class AdminTopics(str, Enum):
    AGENCY = "agency"
    CARRIER = "carrier"
    ALL = "all"
