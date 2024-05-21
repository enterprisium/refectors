from fastapi import APIRouter, HTTPException, status, BackgroundTasks, UploadFile, Query
from .Schema import GeneratorRequest
from .utils.GroqInstruct import chatbot
from .Story.Story import Story
import asyncio, pprint, json
from tqdm import tqdm
from .database.Model import models, database_url, Scene, Project, database
from .utils.RenderVideo import RenderVideo
from .Prompts.StoryGen import Prompt
from App.Editor.editorRoutes import celery_task, EditorRequest


async def update_scene(model_scene):
    await model_scene.generate_scene_data()
    await model_scene.update(**model_scene.__dict__)


async def main(request: GeneratorRequest):
    topic = request.prompt
    renderr = RenderVideo()
    message = chatbot(Prompt.format(topic=topic))

    generated_story = Story.from_dict(message["scenes"])

    print("Generated Story ✅")

    x = await Project.objects.create(name=topic[0:100])

    # Assuming generated_story.scenes is a list of scenes
    scene_updates = []
    with tqdm(total=len(generated_story.scenes)) as pbar:
        for i in range(0, len(generated_story.scenes), 2):
            batch = generated_story.scenes[i : i + 2]  # Get a batch of two story scenes
            batch_updates = []

            for story_scene in batch:
                model_scene = await Scene.objects.create(project=x)
                model_scene.image_prompts = story_scene.image_prompts
                model_scene.narration = story_scene.narration
                await model_scene.update(**model_scene.__dict__)
                batch_updates.append(
                    update_scene(model_scene)
                )  # Append update coroutine to batch_updates
            scene_updates.extend(batch_updates)  # Accumulate updates for later awaiting
            await asyncio.gather(
                *batch_updates
            )  # Await update coroutines for this batch
            pbar.update(len(batch))  # Increment progress bar by the size of the batch

    temp = await x.generate_json()
    # print(temp)

    # await renderr.render_video(temp)
    request = EditorRequest.model_validate(temp)
    await celery_task(video_task=request)


generator_router = APIRouter(tags=["video-Generator"])


@generator_router.post("/generate_video")
async def generate_video(
    videoRequest: GeneratorRequest, background_task: BackgroundTasks
):
    background_task.add_task(main, videoRequest)
    return {"task_id": "started"}
