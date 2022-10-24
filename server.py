import asyncio
import os
from dataclasses import dataclass
from fastapi import FastAPI, Request, BackgroundTasks
import logging
import os
from time import time
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
from pixel_art_diffusion import generate as generate

PROMPT_TAGS = ["pixelart", "bg"]

logging.basicConfig(level=logging.INFO, format="%(levelname)-9s %(asctime)s - %(name)s - %(message)s")
LOGGER = logging.getLogger(__name__)

EXPERIMENTS_BASE_DIR = "/experiments/"
QUERY_BUFFER = {}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)
loop = asyncio.get_event_loop()

@dataclass
class Query():
    query_name: str
    query_sequence: str
    s: str
    steps: int
    seed: int
    result: str = ""
    extention: str = ".glb"
    experiment_id: str = None
    status: str = "pending"

    def __post_init__(self):
        self.experiment_id = str(time())
        self.experiment_dir = os.path.join(EXPERIMENTS_BASE_DIR, self.experiment_id)

@app.get("/prompt_tags")
def get_tags(request: Request):
    return PROMPT_TAGS

@app.get("/generate")
async def root(request: Request, background_tasks: BackgroundTasks, s: str, steps: int, seed: int):
    print(type(seed))
    query = Query(query_name="test", query_sequence=5, s = s, steps = steps, seed = seed)
    QUERY_BUFFER[query.experiment_id] = query
    background_tasks.add_task(process, query)
    LOGGER.info(f'root - added task')
    return {"id": query.experiment_id}

@app.get("/generate_result")
async def result(request: Request, query_id: str):
    if query_id in QUERY_BUFFER:
        if QUERY_BUFFER[query_id].status == "done":
            resp = FileResponse(QUERY_BUFFER[query_id].result, filename="output.png")
            print(resp)
            del QUERY_BUFFER[query_id]
            return resp
        return {"status": QUERY_BUFFER[query_id].status}
    else:
        return {"status": "finished"}

def process(query):
    LOGGER.info(f"process - {query.experiment_id} - Submitted query job. Now run non-IO work for 10 seconds...")
    res = generate(input_prompt=QUERY_BUFFER[query.experiment_id].s, input_steps=QUERY_BUFFER[query.experiment_id].steps, input_seed=QUERY_BUFFER[query.experiment_id].seed)
    
    QUERY_BUFFER[query.experiment_id].status = "done"
    QUERY_BUFFER[query.experiment_id].result = "./outputs/" + res
    LOGGER.info(f'process - {query.experiment_id} - done!')

@app.get("/backlog/")
def return_backlog():
    return {f"return_backlog - Currently {len(QUERY_BUFFER)} jobs in the backlog."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7777)