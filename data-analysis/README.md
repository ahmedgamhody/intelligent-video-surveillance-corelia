# API Structure

```bash

├── streamlit                   # directory for streamlit code for analysis dashboard
│    ├── .streamlit
│    │   └── secrets.toml
│    │
│    ├── connect_db.py
│    ├── app.py
│    └── anomaly_detection.py
│
├── venv                    # directory for virtual env, It's required for docker compose 
├── dockerfile              # docker file for production
├── Makefile                # Make file to help create docker images
├── requirements.txt        # requirements file for all dependencies
└── README.md               # ...
```