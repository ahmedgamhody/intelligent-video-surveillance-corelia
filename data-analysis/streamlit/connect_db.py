import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import os
from dotenv import load_dotenv

# Load from .env
load_dotenv("../../.env")

# Now use them like:
db_user = os.getenv("IVS_SERVICE_DB_USER")
db_pass = os.getenv("IVS_SERVICE_DB_PASS")
db_port = os.getenv("IVS_SERVICE_DB_PORT")
db_name = os.getenv("IVS_SERVICE_DB_NAME")

print(f"postgresql+psycopg2://{db_user}:{db_pass}@localhost:{db_port}/{db_name}")


def load_data():
    try:
        engine = create_engine(f"postgresql+psycopg2://{db_user}:{db_pass}@localhost:{db_port}/{db_name}")

        query = "SELECT timestamp, channel_name, source_name, boxes FROM public.surveillance"
        df = pd.read_sql(query, engine)
        df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)

        # Drop rows where boxes is not a list or has length <= 1
        df = df[df['boxes'].apply(lambda x: isinstance(x, list) and len(x) > 1)]

        df_exploded = df.explode('boxes').reset_index(drop=True)

        # Ensure each box has 7 elements
        boxes_list = df_exploded['boxes'].tolist()
        valid_boxes = [b if isinstance(b, list) and len(b) == 7 else [None]*7 for b in boxes_list]

        box_df = pd.DataFrame(valid_boxes, columns=['x1', 'y1', 'x2', 'y2', 'object_conf', 'object_class', 'object_id'])
        box_df['object_box'] = box_df[['x1', 'y1', 'x2', 'y2']].values.tolist()

        df_final = pd.concat([df_exploded.drop(columns=['boxes']), box_df[['object_class', 'object_id', 'object_conf', 'object_box']]], axis=1)
        
        return df_final

    except Exception as e:
        st.title("No Database")
        return None