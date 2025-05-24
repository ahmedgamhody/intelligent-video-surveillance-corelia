import asyncio
from services import Predict


class Channel:
    object: Predict
    asyncio_task: asyncio.Task
    runnig_state: bool = True
    more_instences: int = 0
