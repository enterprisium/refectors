import databases
import orm
import asyncio, os
import uuid, random
from pydub import AudioSegment
from .DescriptAPI import Speak
from .Vercel import AsyncImageGenerator
import aiohttp
from typing import List
from pydantic import BaseModel
import json

database_url = "sqlite+aiosqlite:///ok.db"
database = databases.Database(database_url)
models = orm.ModelRegistry(database=database)


class WordAlignment(BaseModel):
    text: str
    alignedWord: str
    start: float
    end: float
    hasFailedAlignment: bool

    @classmethod
    def from_old_format(cls, data: dict, offset: float = 0.0):
        return cls(
            text=data["word"],
            alignedWord=data["alignedWord"],
            start=data["startTime"] + offset,
            end=data["endTime"] + offset,
            hasFailedAlignment=data["hasFailedAlignment"],
        )


def transform_alignment_data(data: List[dict], offset: float = 0.0) -> List[dict]:
    return [WordAlignment.from_old_format(item, offset).model_dump() for item in data]


class Project(orm.Model):
    tablename = "projects"
    start = 0
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "name": orm.String(max_length=10_000),
        "aspect_ratio": orm.Float(allow_null=True, default=0),
        "transcript": orm.JSON(allow_null=True, default=[]),
        "duration": orm.Integer(allow_null=True, default=0),
        "assets": orm.JSON(allow_null=True, default=[]),
        "links": orm.JSON(allow_null=True, default=[]),
        "constants": orm.JSON(allow_null=True, default={}),
    }

    async def get_all_scenes(self):
        return await Scene.objects.filter(project=self).all()

    async def generate_json(self):
        project_scenes: List[Scene] = await self.get_all_scenes()
        self.links = []
        self.assets = []
        image_assets = []
        video_assets = []
        audio_assets = []
        text_stream = []

        transitions = [
            # "WaveRight_transparent.webm",
            # "WaveLeft_transparent.webm",
            # "WaveBlue_transparent.webm",
            # "Wave_transparent.webm",
            # "Swirl_transparent.webm",
            # "Snow_transparent.webm",
            # "Likes_transparent.webm",
            # "Lightning_transparent.webm",
            "Happy_transparent.webm",
            # "Fire_transparent.webm",
            # "CurlingWave_transparent.webm",
            # "Cloud_transparent.webm",
        ]

        self.links.append(
            {
                "file_name": "sfx_1.mp3",
                "link": "https://dm0qx8t0i9gc9.cloudfront.net/previews/audio/BsTwCwBHBjzwub4i4/click-match_My50GP4u_NWM.mp3?type=preview&origin=AUDIOBLOCKS&timestamp_ms=1715843203035&publicKey=kUhrS9sKVrQMTvByQMAGMM0jwRbJ4s31HTPVkfDGmwGhYqzmWJHsjIw5fZCkI7ba&organizationId=105711&apiVersion=2.0&stockItemId=28820&resolution=&endUserId=414d29f16694d76c58e7998200a8dcf6f28dc165&projectId=f734c6d7-e39d-4c1d-8f41-417f94cd37ce&searchId=adb77624-5919-41ee-84c6-58e7af098a6d&searchPageId=9124f65b-3e21-47ac-af6b-81387328b7b5",
            }
        )
        for scene in project_scenes:
            _, file_name = os.path.split(scene.narration_path)
            self.duration += scene.narration_duration  ## added one for spaces
            self.links.append({"file_name": file_name, "link": scene.narration_link})

            # generate transcripts
            temp = await scene.generate_scene_transcript(offset=self.start)
            end_word = temp[-1]

            # narration of the story
            audio_assets.append(
                {
                    "type": "audio",
                    "name": file_name,
                    "start": self.start,
                    "end": end_word["start"],
                    "props": {
                        "startFrom": 0,
                        "endAt": end_word["start"] * 30,
                        # "volume": 5,
                    },
                }
            )
            text_stream.extend(temp[:-1])

            ## images and transitions
            for image in scene.images:
                file_name = str(uuid.uuid4()) + ".png"
                self.links.append({"file_name": file_name, "link": image})
                image_assets.append(
                    {
                        "type": "image",
                        "name": file_name,
                        "start": self.start,
                        "end": self.start + scene.image_duration,
                    }
                )
                self.start = self.start + scene.image_duration

                ## transitions between images
                video_assets.append(
                    {
                        "type": "video",
                        "name": "Effects/" + random.choice(transitions),
                        "start": self.start - 1,
                        "end": self.start + 2,
                        "props": {
                            "startFrom": 1 * 30,
                            "endAt": 3 * 30,
                            "volume": 0,
                        },
                    }
                )

        self.assets.append({"type": "audio", "sequence": audio_assets})
        ## add the images to assets
        self.assets.append({"type": "image", "sequence": image_assets})
        self.assets.append(
            {"type": "video", "sequence": video_assets},
        )
        self.constants = {
            "duration": self.duration * 30,
            "height": 1920,
            "width": 1080,
        }
        self.assets.append({"type": "text", "sequence": text_stream})

        await self.update(**self.__dict__)
        return {"links": self.links, "assets": self.assets, "constants": self.constants}


class Scene(orm.Model):
    tts = Speak()
    tablename = "scenes"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "project": orm.ForeignKey(Project),
        "images": orm.JSON(default=None),
        "narration": orm.String(max_length=10_000, allow_null=True, default=""),
        "image_prompts": orm.JSON(default=None),
        "narration_duration": orm.Float(allow_null=True, default=0),
        "image_duration": orm.Float(allow_null=True, default=0),
        "narration_path": orm.String(
            max_length=100,
            allow_null=True,
            default="",
        ),
        "narration_link": orm.String(max_length=10_000, allow_null=True, default=""),
    }

    async def generate_scene_transcript(self, offset):
        links = [self.narration_link]
        text = self.narration + " master"
        transcript = await self.tts._make_transcript(links=links, text=text)
        return transform_alignment_data(data=transcript, offset=offset)

    async def generate_scene_data(self):
        # Run narrate() and generate_images() concurrently
        await asyncio.gather(self.narrate(), self.generate_images())
        self.calculate_durations()

    async def narrate(self):
        link, path = await self._retry_narration_generation()
        self.narration_path = path
        self.narration_link = link

    async def _retry_narration_generation(self):

        retry_count = 0
        while retry_count < 3:
            try:
                return await self.tts.say(
                    text=self.narration + " master"
                )  ### The blanks help to even stuff up.
            except Exception as e:
                print(f"Failed to generate narration: {e}")
                retry_count += 1
                await asyncio.sleep(1)  # Add delay before retrying

        print("Failed to generate narration after 3 attempts.")

    def calculate_durations(self):
        wav_file = AudioSegment.from_file(self.narration_path, format="wav")
        self.narration_duration = int(len(wav_file) / 1000)
        self.image_duration = self.narration_duration / len(self.image_prompts)

    async def generate_images(self):
        self.images = []
        async with aiohttp.ClientSession() as session:
            image_generator = AsyncImageGenerator(session)
            for payload in self.image_prompts:
                result = await image_generator.generate_image(payload)
                status = await image_generator.fetch_image_status(result["id"])
                self.images.extend(status["output"])


class Transition(orm.Model):
    tablename = "transitions"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "name": orm.String(max_length=100),
        "file_path": orm.String(max_length=100),
    }


class BackgroundMusic(orm.Model):
    tablename = "background_music"
    registry = models
    fields = {
        "id": orm.Integer(primary_key=True),
        "name": orm.String(max_length=100),
        "file_path": orm.String(max_length=100),
    }


# class Testy(orm.Model):
#     tablename = "asd"
#     registry = models
#     fields = {
#         "id": orm.Integer(primary_key=True),
#         "duration": orm.Float(allow_null=True,default=None),
#         "area": orm.Float(allow_null=True,default=None),
#         "radius": orm.Float(allow_null=True,default=None),
#     }

#     def calculate_durations(self):
#         self.area = self.radius**2 * 3.14
#         pass


# # Create the tables
async def create_tables():
    datas = {
        "narration": "Welcome to a journey through some of history's strangest moments! Get ready to explore the bizarre, the unusual, and the downright weird.",
        "image_prompts": [
            "Vintage book opening, revealing strange facts, mixed media collage, curious and intriguing, mysterious, eccentric, macro lens, soft lighting, conceptual photography, cross-processed film, surreal, warm tones, textured paper."
        ],
    }

    await models._create_all(database_url)
    x = await Project.objects.create(name="avatar")
    scene = await Scene.objects.create(project=x)
    scene.narration = datas["narration"]
    scene.image_prompts = datas["image_prompts"]

    await scene.generate_scene_data()
    await scene.objects.update(**scene.__dict__)
    p = await x.get_all_scenes()
    print(p)
    print(scene.__dict__)


# asyncio.run(create_tables())
# # Run the function to create tables
# await create_tables()

# # Example usage:
# await Note.objects.create(text="Buy the groceries.", completed=False)
# note = await Note.objects.get(id=1)
# print(note)
