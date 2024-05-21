from pydantic import BaseModel
from typing import List, Optional
from pydantic import validator
import os, json


class Assets(BaseModel):
    type: str
    sequence: List[dict]

    @validator("type")
    def valid_type(cls, v):
        if v not in ["video", "audio", "text", "image", "sfx", "background"]:
            raise ValueError("Invalid asset type")
        return v


def CreateFiles(assets: List[Assets], asset_dir: str):
    for asset in assets:
        filename = f"{asset.type.capitalize()}Sequences.json"
        # Convert dictionary to JSON string
        json_string = json.dumps(asset.sequence)

        # Create directory if it doesn't exist
        os.makedirs(asset_dir, exist_ok=True)
        print(os.path.join(asset_dir, filename))
        # Write JSON string to file
        with open(os.path.join(asset_dir, filename), "w") as f:
            f.write(json_string)
