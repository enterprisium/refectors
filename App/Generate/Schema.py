from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from pydantic import validator


class GeneratorRequest(BaseModel):
    prompt: str
