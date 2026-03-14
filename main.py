from random import randint

from fastapi import FastAPI,HTTPException, Request, Response
from datetime import datetime
from typing import Any


app = FastAPI(root_path="/api/v1")

@app.get("/")
async def root():
    return {"message":"Hello world!"}

data : Any = [
    {
        "campaign_id": 1,
        "name":"Summer Launch",
        "due_date":datetime.now(),
        "created_at":datetime.now()
    },
    {
        "campaign_id": 2,
        "name":"Friday",
        "due_date":datetime.now(),
        "created_at":datetime.now()
    }
]

@app.get("/campaigns")
async def read_campaigns():
    return {"campaigns":data}

@app.get("/campaigns/{id}")
async def read_campaigns(id:int):
    for campaign in data:
        if campaign.get("campaign_id")==id:
            return {"campaigns": campaign}
    raise HTTPException(status_code=404)


@app.post("/campaigns" , status_code=201)
async def create_Campaign(body: dict[str, Any]):

    new : Any = {
        "campaign_id": randint(100,1000),
        "name":body.get("name"),
        "due_date":body.get("due_date"),
        "created_at":datetime.now()

    }
    data.append(new)
    return {"campaign":new}

@app.put("/campaigns/{id}",)
async def update_campaign(id: int,body:dict[str,Any]):

    for i, campaign in enumerate(data):
        if campaign.get("campaign_id")==id:

            updated : Any = {
                "campaign_id": id,
                "name":body.get("name"),
                "due_date":body.get("due_date"),
                "created_at":campaign.get("created_at")
            }
            data[i] = updated
            return {"campaign": updated}
    raise HTTPException(status_code=404)

@app.delete("/campaigns/{id}",)
async def update_campaign(id: int):

    for i, campaign in enumerate(data):
        if campaign.get("campaign_id")==id:
            data.pop(i)
            return Response(status_code=204)

            return {"campaign": updated}
    raise HTTPException(status_code=404)



