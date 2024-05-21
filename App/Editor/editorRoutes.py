from fastapi import APIRouter, HTTPException, status, BackgroundTasks, UploadFile, Query
from .Schema import EditorRequest, TaskInfo
from App.Worker import celery_task, concatenate_videos
from celery.result import AsyncResult
import aiofiles, os, uuid, aiohttp
from App import SERVER_STATE, Task

videditor_router = APIRouter(tags=["vidEditor"])


@videditor_router.post("/create-video")
async def create_video(videoRequest: EditorRequest, background_task: BackgroundTasks):
    background_task.add_task(celery_task, videoRequest)
    return {"task_id": "started"}


@videditor_router.post("/create-chunks")
async def create_chunks(videoRequest: EditorRequest, background_task: BackgroundTasks):
    video_duration = videoRequest.constants.duration
    task_id = uuid.uuid4()
    new_task = Task(TASK_ID=task_id)

    active_nodes = [
        node
        for node in SERVER_STATE.NODES
        if await new_task._check_node_online(node.SPACE_HOST)
    ]
    number_of_nodes = len(active_nodes)
    ranges = [
        [i, i + number_of_nodes] for i in range(0, video_duration, number_of_nodes)
    ]
    for i, node in enumerate(active_nodes):
        await new_task.add_node(node, i)

    SERVER_STATE.TASKS[task_id] = new_task

    async with aiohttp.ClientSession() as session:
        for i, node in enumerate(active_nodes):
            videoRequest.constants.frames = ranges[i]
            if node.SPACE_HOST == SERVER_STATE.SPACE_HOST:
                background_task.add_task(celery_task, videoRequest)
            async with session.post(
                "node.SPACE_HOST/create-video", json=videoRequest
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail="Failed to post request to node",
                    )

    return {"task_id": "started"}


@videditor_router.post("/uploadfile/")
async def create_file(
    background_tasks: BackgroundTasks,
    file: UploadFile,
    node: str,
    chunk: int,
    task: str,
):

    chunk_directory = f"/tmp/Video/{task}"
    file_name = f"{chunk_directory}/{chunk}.mp4"
    # Create the directory if it does not exist
    os.makedirs(chunk_directory, exist_ok=True)

    try:
        async with aiofiles.open(file_name, "wb") as f:
            while contents := await file.read(1024 * 1):
                await f.write(contents)

    except Exception as e:
        return {
            "message": f"There was an error uploading the file, error message {str(e)}  "
        }
    finally:
        await file.close()
    running_task = SERVER_STATE.TASKS[task]
    running_task.mark_node_completed(node)
    if running_task.is_completed():
        background_tasks.add_task(concatenate_videos, chunk_directory)

    return {"message": "File uploaded successfully"}
