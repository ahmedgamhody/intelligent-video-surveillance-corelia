# IVS

Intelligent Video Surveillance

## Table of content

- [IVS](#IVS)
  - [Table of content](#table-of-content)
  - [Ports](#ports)
  - [Development](#development)
    - [Prerequisites](#prerequisites)
    - [Configuration](#configuration)
    - [Run instructions](#run-instructions)
  - [Docker instructions](#docker-instructions)
    - [For Development](#for-development)
    - [For Production](#for-production)
      - [Build image](#build-image)
      - [Publish image](#publish-image)
  - [API Details](#api-details)
  
## Ports
- frontend: 1234
- backend: 2345
- data-scince: 3456
- data-analysis: 4567

- ivs_system_data (postgredb): 5678
- ivs_service_data (timescaledb): 6789
- ivs_kafka (kraft): 7890


## Development
### Prerequisites
- Python v3.12 # for data-science, data-analysis and backend
- node.js v24 # for frontend

### Configuration
- rename example.env to .env 
- Adapt `.env` file

### Run instructions
- docker and databases:
  - run `docker compose up -d`
  - create ivs_system_database `psql -h localhost -p <port> -U <user> -d <db_name> -f ./backend/src/database/create_db.sql`
  - create ivs_service_database `psql -h localhost -p <port> -U <user> -d <db_name> -f ./data-science/src/database/create_db.sql`
- data-science: in new terminal: `cd data-science`
  - create data-science venv `python -m venv venv`
  - activate data-science venv `source venv/bin/acivate`
  - install requirements `pip isntall -r requirements.txt`
  - run data-science `cd src`, `python main.py` or in background using `nohup python main.py &`
- data-analysis: in new terminal: `cd data-analysis`
  - create data-analysis venv `python -m venv venv`
  - activate data-analysis venv `source venv/bin/acivate`
  - install requirements `pip isntall -r requirements.txt`
  - run data-analysis `cd streamlit`, `streamlit run app.py --server.port 4567` or in background using `nohup streamlit run app.py --server.port 4567 &`
- backend: in new terminal: `cd backend`
  - create backend venv `python -m venv venv`
  - activate backend venv `source venv/bin/acivate`
  - install requirements `pip isntall -r requirements.txt`
  - run backend `cd src`, `python main.py` or in background using `nohup python main.py &`
- frontend: in new terminal: `cd frontend`
  - install requirements `npm install`
  - run frontend `npm run dev` or in background using `nohup npm run dev &`

## Docker instructions
### For Development

- Start container

```sh
docker compose -f docker-compose.yml up -d
```

- End container

```sh
docker compose -f docker-compose.yml down -v
```

### For Production
#### Build image

```sh
make build
```

#### Publish image

```sh
make publish
```