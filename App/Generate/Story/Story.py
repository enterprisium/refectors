import json
from pydantic import BaseModel
from typing import List


class Scene(BaseModel):
    narration: str
    image_prompts: List[str]

    def num_images(self):
        return len(self.image_prompts)


class Story(BaseModel):
    scenes: List[Scene]

    @classmethod
    def from_dict(cls, data):
        # Parse JSON string into list of dictionaries
        json_data = data
        for item in json_data:
            if "image_prompts" in item and "narration" not in item:
                for key in item.keys():
                    if key != "image_prompts":
                        item["narration"] = item.pop(key)
                        break

        # Convert JSON data into list of Scene objects
        scenes = [Scene(**item) for item in json_data]
        # Return Story object with all scenes
        return cls(scenes=scenes)

    @classmethod
    def parse_markdown(cls, markdown_str):
        # Extract JSON part from markdown string
        try:
            json_str = markdown_str.split("```json")[1].split("```")[0].strip()
        except:
            pass
        return cls.from_dict(data=json.loads(json_str))

    @property
    def all_narrations(self):
        return [scene.narration for scene in self.scenes]

    @property
    def all_images(self):
        # return [scene.images_prompt for scene in self.scenes]
        results = []
        for scene in self.scenes:
            results.extend(scene.images_prompt)
        return results

    def num_images_in_scene(self, scene_index):
        return self.scenes[scene_index].num_images()
