from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from pydantic import validator


class LinkInfo(BaseModel):
    file_name: str
    link: HttpUrl


class Constants(BaseModel):
    task: Optional[str] = ""
    chunk: Optional[int] = 0
    duration: Optional[int]
    height: Optional[int]
    width: Optional[int]
    text: Optional[dict] = {}
    frames: Optional[dict] = {}
    instructions: Optional[bool] = False


class Assets(BaseModel):
    type: str
    sequence: List[dict]

    @validator("type")
    def valid_type(cls, v):
        if v not in ["video", "audio", "text", "image", "sfx", "background"]:
            raise ValueError("Invalid asset type")
        return v


class EditorRequest(BaseModel):
    links: Optional[List[LinkInfo]]  # List of LinkInfo objects
    assets: List[Assets]
    constants: Optional[Constants]


class TaskInfo(BaseModel):
    task_id: str
    progress: int
    completed_tasks: List[str]
