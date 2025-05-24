# API Structure

```bash

├── src                     # directory for source code for the whole API logic 
│    ├── config                 # dir for app configuration
│    │   ├── __init__.py            # Init file
│    │   ├── app_setting.py         # file that contain app settings (APP_ROOT, APP_NAME, ...)
│    │   └── db_setting.py          # file that contain database settings (DB_DSN)
│    │
│    ├── database               # data storage system
│    │   ├── business_storage       # data storage system related to business
│    │   │   ├── __init__.py        # Init file
│    │   │   ├── create_db.sql      # SQL to create postgres functiona
│    │   │   └── db_control.py      # DB interaction functions (insert, update, delete)
│    │
│    ├── schemas                # dir for app schemas
│    │   ├── __init__.py            # Init file
│    │   └── schema.py              # file that contain business schemas (users, channels, sources, models)
│    │
│    ├── routes                 # dir for routes and init for fastAPI
│    │   ├── __init__.py            # Init file
│    │   ├── x.py                   # file that contain ... endpoints
│    │   └── y.py                   # file that contain ... endpoints
│    │
│    └── main.py                # runner file : to start the server using it.
│
├── venv                    # directory for virtual env, It's required for docker compose 
├── dockerfile              # docker file for production
├── Makefile                # Make file to help create docker images
├── requirements.txt        # requirements file for all dependencies
└── README.md               # ...
```