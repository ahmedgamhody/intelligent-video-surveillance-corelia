# API Structure

```bash

├── src                     # directory for source code for the whole API logic 
│    ├── config                 # dir for app configuration
│    │   ├── __init__.py            # Init file
│    │   ├── app_setting.py         # file that contain app settings (APP_ROOT, APP_NAME, ...)
│    │   └── db_setting.py          # file that contain database settings (DB_DSN, KAFKA_BROKER, KAFKA_TOPIC)
│    │
│    ├── database               # ivs_service_data
│    │   ├── __init__.py            # Init file
│    │   ├── create_db.sql          # SQL to create TimescaleDB functiona
│    │   ├── db_control.py          # DB interaction functions (push, get, pull)
│    │   ├── kafka_producer.py      # Push messages to Kafka
│    │   └── kafka_consumer.py      # Consume from Kafka and write to TimescaleDB
│    │
│    ├── schemas                # dir for app schemas
│    │   ├── __init__.py            # Init file
│    │   └── channel_schema.py      # file that contain predictor schema(Channel)
│    │
│    ├── routes                 # dir for routes and init for fastAPI
│    │   ├── __init__.py            # Init file
│    │   └── predictor.py           # file that contain predictor services endpoints
│    │
│    ├── services               # dir to store main services
│    │   ├── __init__.py            # Init file
│    │   ├── inference              # contain main files for inference servevices
│    │   │   ├── __init__.py            # Init file
│    │   │   └── predictor.py           # main service
│    │   ├── export                 # contain files for services to use from cli to export models to different formats
│    │   │   ├── yolo_export.py         # to export yolo models from ",pt" to (".onnx", ".engin", or "torchscript")
│    │   │   └── reid_export.py         # to export reid models from ",pt" to (".onnx", ".engin", or "torchscript")
│    │   └── training               # contain files for services to use from cli to fine-tune models on specific dataset
│    │       └── fine_tune.py           # to fine-tune pre-trained models on dataset
│    │
│    ├── static                 # dir to store project assests (Optional)
│    │   ├── models                 # dir to store models (Optional)
│    │   └── runs                   # dir to store temp files while runing (Optional)
│    │
│    └── main.py                # runner file : to start the server using it.
│
├── venv                    # directory for virtual env, It's required for docker compose 
├── Dockerfile              # docker file for production
├── Makefile                # Make file to help create docker images
├── requirements.txt        # requirements file for all dependencies
└── README.md               # ...
```