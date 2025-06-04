from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi import Form, UploadFile, File
from typing import Dict, List, Optional
import asyncio
import json

from services import Predict
from schemas import Channel
from database import db_controller, kafka_producer


channels: Dict[str, Channel] = {}


predictor = APIRouter(
    prefix="/predictor",
    tags=["Predictor"]
)


@predictor.post("/start_channel")
async def start_channel(channel_name: str = Form(...),
                      models: Optional[str] = Form([]),
                      sources_names: Optional[str] = Form([]),
                      urls_sources: Optional[str] = Form([]),
                      files_sources: Optional[List[UploadFile]] = File([]),
                      confidence_threshold: Optional[int] = Form(25), overlapping_threshold: Optional[int] = Form(75),
                      realtime_mode: Optional[bool] = Form(True), augmentation_mode: Optional[bool] = Form(False),
                      tracking: Optional[bool] = Form(True), reid: Optional[bool] = Form(False)
                      ):
    try:
        assert channel_name not in channels.keys(), KeyError(f"Channel name '{channel_name}' is already exist!")

        models = {model["name"]: {"task": model["task"], "weight": model["weight"]} for model in json.loads(models)}

        sources_names = json.loads(sources_names)
        urls_sources = json.loads(urls_sources)
        files_sources = [file.file for file in files_sources]

        assert len(sources_names) == len(urls_sources) + len(files_sources), KeyError("Must Upload sources with thier names!")
        sources = dict(zip(sources_names, urls_sources + files_sources))

        assert 0 <= confidence_threshold <= 100, ValueError("Confidence threshold must be in range 0 to 100")
        assert 0 <= overlapping_threshold <= 100, ValueError("Overlapping threshold must be in range 0 to 100")
        
        channel = Predict(sources=sources, models=models)
        channel.configure_inference(
            confidence_threshold = confidence_threshold / 100,
            overlapping_threshold = overlapping_threshold / 100,
            augmentation_mode = augmentation_mode,
            realtime_mode = realtime_mode
        )
        channel.config_tracker(tracking, reid)

        channels[channel_name] = Channel
        channels[channel_name].object = channel

        async def run_channel():
            while channels[channel_name].runnig_state:
                data = channels[channel_name].object.run()
                await kafka_producer.push(channel_name, data)
                await asyncio.sleep(0.001)

        channels[channel_name].asyncio_task = asyncio.create_task(run_channel())

        return {"detail": f"Channel '{channel_name}' created and running"}
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@predictor.post("/pause_channel")
async def pause_channel(channel_name: str = Form(...)):
    try:
        assert channel_name in channels.keys(), KeyError("Channel name {channel_name} is not exist!")
        channels[channel_name].runnig_state = False
        return {"detail": f"Channel {channel_name} already paused"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@predictor.post("/resume_channel")
async def resume_channel(channel_name: str = Form(...)):
    try:
        assert channel_name in channels.keys(), KeyError("Channel name {channel_name} is not exist!")
        channels[channel_name].state = True
        return {"detail": f"Channel {channel_name} already resumed"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@predictor.post("/end_channel")
async def end_channel(channel_name: str = Form(...)):
    try:
        assert channel_name in channels.keys(), KeyError("Channel name {channel_name} is not exist!")
        channels[channel_name].asyncio_task.cancel()
        del channels[channel_name]
        return {"detail": f"Channel {channel_name} already deleted"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@predictor.post("/get_channel")
async def get_channel(channel_name: str = Form(...), start: float = Form(...), end: float = Form(...)):
    try:
        assert channel_name in channels.keys(), KeyError("Channel name {channel_name} is not exist!")
        data = await db_controller.get(channel_name, start, end)
        return data
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@predictor.websocket("/connect_channel")
async def connect_channel(websocket: WebSocket, channel_name: str):
    if channel_name not in channels.keys():
        raise HTTPException(status_code=500, detail=f"Channel name {channel_name} is not exist!")
    async def receive():
        try:
            while channel_name in channels.keys():
                user_input = dict(await websocket.receive_json())
                print(user_input)

                # if 'append_sources' in user_input.keys():
                #     for name, source in user_input['append_sources']:
                #         channels[channel_name].object.append_source(name, source)

                # if 'delete_sources' in user_input.keys():
                #     for name in user_input['delete_sources']:
                #         channels[channel_name].object.delete_source(name)
                
                # if 'append_models' in user_input.keys():
                #     for name, parameters in user_input['append_models']:
                #         channels[channel_name].object.append_model(name, parameters)

                # if 'delete_models' in user_input.keys():
                #     for name in user_input['delete_models']:
                #         channels[channel_name].object.delete_model(name)
                
                if 'configure_inference' in user_input.keys():
                    channels[channel_name].object.configure_inference(**user_input['configure_inference'])
                
                if 'configure_tracker' in user_input.keys():
                    channels[channel_name].object.config_tracker(**user_input['configure_tracker'])

                if 'more_instences' in user_input.keys():
                    channels[channel_name].more_instences = user_input['more_instences']
        
        except WebSocketDisconnect:
            pass

    async def send():
        try:
            while channel_name in channels.keys():
                if channels[channel_name].runnig_state:
                    pulled_data = await db_controller.pull(channel_name, more_instances=channels[channel_name].more_instences)
                    await websocket.send_json(pulled_data)
                await asyncio.sleep(0.001)
        except Exception as e:
            pass

    await websocket.accept()
    await asyncio.gather(receive(), send())
