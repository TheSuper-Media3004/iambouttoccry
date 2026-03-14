from contextlib import asynccontextmanager
from random import randint

from fastapi import Depends, FastAPI,HTTPException, Request
from datetime import datetime, timezone
from typing import Annotated, Any, Generic, TypeVar

from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Session, create_engine, select



class Campaign(SQLModel, table=True):
    campaign_id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    due_date: datetime | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=True, index=True)

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    with Session(engine) as session:
        if not session.exec(select(Campaign)).first():
            session.add_all([
                Campaign(name="Summer Launch", due_date=datetime.now()),
                Campaign(name="BLACK FRIDAY", due_date=datetime.now())
            ])
            session.commit()         
    yield

app = FastAPI(root_path="/api/v1", lifespan=lifespan)





@app.get("/")
async def root():
    return {"message":"Hello world!"}

# data : Any = [
#     {
#         "campaign_id": 1,
#         "name":"Summer Launch",
#         "due_date":datetime.now(),
#         "created_at":datetime.now()
#     },
#     {
#         "campaign_id": 2,
#         "name":"Friday",
#         "due_date":datetime.now(),
#         "created_at":datetime.now()
#     }
# ]
T = TypeVar("T")
class Response(BaseModel, Generic[T]):
    data : T

class CampaignCreate(SQLModel):
    name : str
    due_date: datetime | None = None

    

@app.get("/campaigns",response_model=Response[list[Campaign]])
async def read_campaigns(session: SessionDep):
    data = session.exec(select(Campaign)).all()
    return {"data":data}

@app.get("/campaigns/{id}")
async def read_campaigns(id:int, session: SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    return {"data":data}

@app.post("/campaigns" , status_code=201, response_model=Response[Campaign])
async def create_Campaign(campaign: CampaignCreate, session: SessionDep):
    db_campaign = Campaign.model_validate(campaign)
    session.add(db_campaign)
    session.commit()
    session.refresh(db_campaign)
    return {"data" : db_campaign}
@app.put("/campaigns/{id}", response_model=Response[Campaign])
async def update_the_campaign(id:int,campaign: CampaignCreate, session: SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    data.name = campaign.name
    data.due_date = campaign.due_date
    session.add(data)
    session.commit()
    session.refresh(data)
    return {"data":data}


@app.delete("/campaigns/{id}",status_code=204)
async def delete_campaign(id: int, session:SessionDep):
    data = session.get(Campaign, id)
    if not data:
        raise HTTPException(status_code=404)
    session.delete(data)
    session.commit()
    
# @app.get("/campaigns")
# async def read_campaigns():
#     return {"campaigns":data}

# @app.get("/campaigns/{id}")
# async def read_campaigns(id:int):
#     for campaign in data:
#         if campaign.get("campaign_id")==id:
#             return {"campaigns": campaign}
#     raise HTTPException(status_code=404)


# @app.post("/campaigns" , status_code=201)
# async def create_Campaign(body: dict[str, Any]):

#     new : Any = {
#         "campaign_id": randint(100,1000),
#         "name":body.get("name"),
#         "due_date":body.get("due_date"),
#         "created_at":datetime.now()

#     }
#     data.append(new)
#     return {"campaign":new}

# @app.put("/campaigns/{id}",)
# async def update_campaign(id: int,body:dict[str,Any]):

#     for i, campaign in enumerate(data):
#         if campaign.get("campaign_id")==id:

#             updated : Any = {
#                 "campaign_id": id,
#                 "name":body.get("name"),
#                 "due_date":body.get("due_date"),
#                 "created_at":campaign.get("created_at")
#             }
#             data[i] = updated
#             return {"campaign": updated}
#     raise HTTPException(status_code=404)

# @app.delete("/campaigns/{id}",)
# async def update_campaign(id: int):

#     for i, campaign in enumerate(data):
#         if campaign.get("campaign_id")==id:
#             data.pop(i)
#             return Response(status_code=204)
#             # return {"campaign": updated}
#     raise HTTPException(status_code=404)



