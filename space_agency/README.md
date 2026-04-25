# Space Agency

## Description

This project simulates a space agency system using RabbitMQ for communication between different components. The system consists of carriers, agencies, and an admin that publishes messages to the carriers and agencies.

## Demo

Below is a demo of the system in action, showing the admin console, two carriers (ALICE and BOB) consuming messages from their respective queues, and two agencies (NASA and SpaceX) publishing jobs to the exchange.

![Demo](resources/messages_exchange.png)

## Architecture

Whole system architecture can be visualized as follows:

```mermaid
graph LR
    %% Professional Palette Class Definitions
    classDef infra fill:#eceff1,stroke:#34495e,stroke-width:2px,color:#34495e;
    classDef exchange fill:#fff8e1,stroke:#ffb300,stroke-width:2px,color:#8d6e63;
    classDef queue fill:#e1f5fe,stroke:#0288d1,stroke-width:1px,color:#01579b;
    classDef publisher fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;
    classDef consumer fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#880e4f;

    subgraph Compose [Docker Compose]
        R["RabbitMQ Container (5672, 15672)"]
    end

    subgraph Broker [RabbitMQ Broker]
        EX(("space-delivery (topic exchange)"))

        subgraph StandardQueues [Service Queues]
            PPL["people_transport"]
            CARGO["cargo_transport"]
            SAT["satellite_deployment"]
        end

        subgraph AdminQueues [Management Queues]
            ADMIN_ALL["admin-all-messages"]
            CARRIER_ADMIN["carrier-admin-name"]
            AGENCY_ADMIN["agency-admin-name"]
        end
    end

    subgraph Apps [Application Processes]
        Agency["Agency (Publisher)"]
        Admin["Admin (Console)"]
        Carrier["Carrier (Consumer)"]
    end

    %% Apply Styles
    class R infra;
    class EX exchange;
    class PPL,CARGO,SAT,ADMIN_ALL,CARRIER_ADMIN,AGENCY_ADMIN queue;
    class Agency,Admin publisher;
    class Carrier consumer;

    %% Infrastructure
    R --- EX

    %% Publishing Flow
    Agency ==>|"routing_key=service"| EX
    Admin ==>|"routing_key=agency/carrier/all"| EX

    %% Exchange Bindings (Internal Logic)
    EX -.->|people_transport| PPL
    EX -.->|cargo_transport| CARGO
    EX -.->|satellite_deployment| SAT
    EX -.->|"#"| ADMIN_ALL
    EX -.->|"carrier, all"| CARRIER_ADMIN
    EX -.->|"agency, all"| AGENCY_ADMIN

    %% Consumption Flow
    PPL ==> Carrier
    CARGO ==> Carrier
    SAT ==> Carrier
    CARRIER_ADMIN ==> Carrier
    AGENCY_ADMIN ==> Agency
    ADMIN_ALL ==> Admin
```

#### Excalidraw diagram architecture:

![Architecture Diagram](resources/architecture_diagram.png)

### How messages flow

- Agencies publish jobs to the `space-delivery` topic exchange using the service name as the routing key (e.g. `people_transport`, `cargo_transport`, `satellite_deployment`).
- The exchange routes messages to service-specific queues bound with the same routing key, and carriers consume from those queues.
- The Admin process publishes admin messages with routing keys `agency`, `carrier` or `all`. Per-node admin queues use names like `carrier-admin-messages-queue-<NAME>` and `agency-admin-messages-queue-<NAME>` and are bound to the exchange for `carrier`/`agency` and `all` messages.
- An `admin-all-messages-queue` is bound to `#` so the Admin console can listen to every message flowing through the exchange.

## Components

- **Admin**: publishes admin broadcasts and listens to the global admin queue. See `src/space_agency/admin/admin.py`.
- **Agency**: generates jobs and publishes them to the exchange (routing_key = service). See `src/space_agency/agency/agency.py`.
- **Carrier**: consumes service queues (its configured services) and a per-carrier admin queue. See `src/space_agency/carrier/carrier.py`.
- **Shared**: RabbitMQ helpers, settings and callbacks live under `src/space_agency/shared/`.

## Running the project

Start the broker via Docker Compose (uses `.env` for `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS`):

```bash
docker compose -f deploy/docker-compose.yaml --env-file .env up --abort-on-container-exit
```

Start a carrier (example):

```bash
uv run carrier --name BOB --first-service "people_transport" --second-service "cargo_transport"
```

Start another carrier:

```bash
uv run carrier --name ALICE --first-service "cargo_transport" --second-service "satellite_deployment"
```

Start agencies:

```bash
uv run agency --name SpaceX
uv run agency --name NASA
```

Start the admin console (it publishes and also listens to the global admin queue):

```bash
uv run admin
```

**Architecture for the above exaple can be visualized as follows:**

```mermaid
graph LR
    %% Class Definitions for Styling
    classDef infra fill:#eceff1,stroke:#34495e,stroke-width:2px,color:#34495e;
    classDef exchange fill:#fff8e1,stroke:#ffb300,stroke-width:2px,color:#8d6e63;
    classDef queue fill:#e1f5fe,stroke:#0288d1,stroke-width:1px,color:#01579b;
    classDef publisher fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;
    classDef consumer fill:#fce4ec,stroke:#c2185b,stroke-width:2px,color:#880e4f;

    subgraph Compose [Docker Compose]
        R["RabbitMQ Container(5672, 15672)"]
    end

    subgraph Broker [RabbitMQ Broker]
        EX(("space-delivery (topic exchange)"))

        subgraph StandardQueues [Service Queues]
            PPL["people_transport"]
            CARGO["cargo_transport"]
            SAT["satellite_deployment"]
        end

        subgraph AdminQueues [Admin & Broadcast Queues]
            ADMIN_ALL["admin-all-messages"]
            ALICE_CARRIER_ADMIN["carrier-admin-ALICE"]
            BOB_CARRIER_ADMIN["carrier-admin-BOB"]
            NASA_AGENCY_ADMIN["agency-admin-NASA"]
            SpaceX_AGENCY_ADMIN["agency-admin-SpaceX"]
        end
    end

    subgraph Apps [Application Processes]
        direction TB
        NASAAgency["NASA Agency (Publisher)"]
        SpaceXAgency["SpaceX Agency (Publisher)"]
        AdminApp["Admin Console (Pub/Sub)"]
        ALICE_CARRIER["ALICE Carrier (Consumer)"]
        BOB_CARRIER["BOB Carrier (Consumer)"]
    end

    %% Apply Styles
    class R infra;
    class EX exchange;
    class PPL,CARGO,SAT,ADMIN_ALL,ALICE_CARRIER_ADMIN,BOB_CARRIER_ADMIN,NASA_AGENCY_ADMIN,SpaceX_AGENCY_ADMIN queue;
    class NASAAgency,SpaceXAgency publisher;
    class ALICE_CARRIER,BOB_CARRIER consumer;
    class AdminApp publisher;

    %% Infrastructure
    R --- EX

    %% Publisher Flows
    NASAAgency ==>|routing_key=service| EX
    SpaceXAgency ==>|routing_key=service| EX
    AdminApp ==>|routing_key=agency / carrier / all| EX

    %% Exchange Bindings
    EX -->|people_transport| PPL
    EX -->|cargo_transport| CARGO
    EX -->|satellite_deployment| SAT
    EX -->|"#"| ADMIN_ALL
    EX -->|"carrier"| BOB_CARRIER_ADMIN
    EX -->|"carrier"| ALICE_CARRIER_ADMIN
    EX -->|"agency"| NASA_AGENCY_ADMIN
    EX -->|"agency"| SpaceX_AGENCY_ADMIN

    %% Consumer Flows
    PPL --> BOB_CARRIER
    CARGO --> BOB_CARRIER
    CARGO --> ALICE_CARRIER
    SAT --> ALICE_CARRIER

    BOB_CARRIER_ADMIN --> BOB_CARRIER
    ALICE_CARRIER_ADMIN --> ALICE_CARRIER
    NASA_AGENCY_ADMIN --> NASAAgency
    SpaceX_AGENCY_ADMIN --> SpaceXAgency
    ADMIN_ALL --> AdminApp
```

#### Excalidraw example architecture diagram:

![Example Architecture Diagram](resources/example_architecture.png)

## Notes

- Exchange name: `space-delivery` (see `src/space_agency/shared/config.py`).
- Service names (routing keys) are defined in `Services` enum: `people_transport`, `cargo_transport`, `satellite_deployment`.
- Queue names and some config variables are defined in `src/space_agency/shared/config.py`.

