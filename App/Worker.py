from celery import Celery, chain
import os, shutil, subprocess
import uuid
from urllib.parse import urlparse
from subprocess import run
from App import celery_config, bot, SERVER_STATE
from typing import List
from App.Editor.Schema import EditorRequest, LinkInfo, Assets, Constants
from celery.signals import worker_process_init
from asgiref.sync import async_to_sync
import json
import os
from pydantic import BaseModel
from App.utilis import upload_file

import subprocess


def concatenate_videos(input_dir):
    # Get a list of all the mp4 files in the input directory
    files = sorted([f for f in os.listdir(input_dir) if f.endswith(".mp4")])

    # Generate the input file list for ffmpeg
    input_files = "|".join([f"file '{os.path.join(input_dir, f)}'" for f in files])

    output_file = f"{input_dir}/final.mp4"
    # Run the ffmpeg command to concatenate the videos
    subprocess.run(
        [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            f"concat:{input_files}",
            "-c",
            "copy",
            output_file,
        ]
    )
    bot.start()
    bot.send_file(-1002069945904, file=output_file, caption="finally done!")
    return output_file


class YouTubeUploadTask(BaseModel):
    filename: str
    title: str = "Default Title"
    description: str = "Default Description"
    category_id: str = "22"  # Default to a generic category, update as needed
    privacy: str = "private"
    tags: str = ""
    thumbnail: str = None


# celery = Celery()
# celery.config_from_object(celery_config)
# celery.conf.update(
#     # Other Celery configuration settings
#     CELERYD_LOG_LEVEL="DEBUG",  # Set log level to DEBUG for the worker
# )


# @celery.task(name="CreateFile")
def create_json_file(assets: List[Assets], asset_dir: str):
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


# @celery.task(name="Constants")
def create_constants_json_file(constants: Constants, asset_dir: str):
    temp_dir = asset_dir.replace("src/HelloWorld/Assets", "")
    instrunction_file = os.path.join(temp_dir, "ServerInstructions.json")
    filename = "Constants.json"
    if constants:
        json_string = json.dumps(constants.dict())
    else:
        json_string = json.dumps({})
    os.makedirs(asset_dir, exist_ok=True)
    with open(instrunction_file, "w") as f:
        if constants.instructions:
            f.write(json.dumps({"frames": constants.frames}))
        else:
            f.write(json.dumps({"frames": [0, constants.duration]}))

    with open(os.path.join(asset_dir, filename), "w") as f:
        f.write(json_string)


def create_symlink(source_dir, target_dir, symlink_name):
    source_path = os.path.join(source_dir, symlink_name)
    target_path = os.path.join(target_dir, symlink_name)

    try:
        os.symlink(source_path, target_path)
        print(f"Symlink '{symlink_name}' created successfully.")
    except FileExistsError:
        print(f"Symlink '{symlink_name}' already exists.")


def download_with_wget(link, download_dir, filename):
    print(["aria2c", link, "-d", download_dir, "-o", filename])
    subprocess.run(["aria2c", link, "-d", download_dir, "-o", filename])
    # os.system(f"aria2c  {link}   -d   {download_dir} -o  {filename}")


# @celery.task(name="CopyRemotion")
def copy_remotion_app(src: str, dest: str):
    shutil.copytree(src, dest)


# @celery.task(name="Unsilence")
def unsilence(directory: str):
    output_dir = os.path.join(directory, "out/video.mp4")
    shortered_dir = os.path.join(directory, "out/temp.mp4")
    os.system(f"pipx run unsilence {output_dir} {shortered_dir} -y")
    os.remove(output_dir)
    os.rename(shortered_dir, output_dir)


# @celery.task(name="InstallDependency")
def install_dependencies(directory: str):
    os.chdir(directory)
    os.system("npm install")


# @celery.task(name="uploadTime")
def upload_video_to_youtube(task_data: dict):
    # Convert dict to Pydantic model
    task = YouTubeUploadTask(**task_data)

    # Build the command
    command = [
        "/srv/youtube/youtubeuploader",  # Adjust the path as needed
        "-filename",
        task.filename,
        "-title",
        task.title,
        "-description",
        task.description,
        "-categoryId",
        task.category_id,
        "-privacy",
        task.privacy,
        "-tags",
        task.tags,
    ]

    if task.thumbnail:
        command.extend(["-thumbnail", task.thumbnail])

    # Execute the command
    result = run(command, capture_output=True, text=True)

    return result.stdout


# @celery.task(name="DownloadAssets")
def download_assets(links: List[LinkInfo], temp_dir: str):
    public_dir = f"{temp_dir}/public"
    for link in links:
        file_link = str(link.link)
        file_name = link.file_name
        download_with_wget(file_link, public_dir, file_name)


# @celery.task(name="RenderFile")
def render_video(directory: str, output_directory: str):
    os.chdir(directory)
    os.system(
        f"npm run build --enable-multiprocess-on-linux --output {output_directory}"
    )
    print("complete")


# @celery.task(name="send")
async def cleanup_temp_directory(
    temp_dir: str,
    output_dir: str,
    video_task: EditorRequest,
    chat_id: int = -1002069945904,
):
    video_folder_dir = f"/tmp/Video/{video_task.constants.task}"

    try:
        print("sending...")
        # bot.send_video(chat_id=chat_id,caption="Your Video Caption",file_name=output_dir)
        await bot.send_file(chat_id, file=output_dir, caption="Your video caption")

    finally:
        # remotion_app_dir = os.path.join("/srv", "Remotion-app")
        # shutil.rmtree(remotion_app_dir)
        # use the cache
        # shutil.copytree(temp_dir, remotion_app_dir)
        # if not SERVER_STATE.CACHED:
        #    SERVER_STATE.CACHED = True
        # Cleanup: Remove the temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)


# @celery.task(name="All")
async def celery_task(video_task: EditorRequest):
    remotion_app_dir = os.path.join("/srv", "Remotion-app")
    project_id = str(uuid.uuid4())
    temp_dir = f"/tmp/{project_id}"
    output_dir = f"/tmp/{project_id}/out/video.mp4"
    assets_dir = os.path.join(temp_dir, "src/HelloWorld/Assets")

    copy_remotion_app(remotion_app_dir, temp_dir)

    # # use the cached stuff
    # if not SERVER_STATE.CACHED:
    #
    install_dependencies(temp_dir)
    create_constants_json_file(video_task.constants, assets_dir)
    create_json_file(video_task.assets, assets_dir)
    download_assets(video_task.links, temp_dir)
    render_video(temp_dir, output_dir)
    # unsilence(temp_dir)
    await cleanup_temp_directory(temp_dir, output_dir, video_task)

    # chain(
    #     copy_remotion_app.si(remotion_app_dir, temp_dir),
    #     install_dependencies.si(temp_dir),
    #     create_constants_json_file.si(video_task.constants, assets_dir),
    #     create_json_file.si(video_task.assets, assets_dir),
    #     download_assets.si(video_task.links, temp_dir) if video_task.links else None,
    #     render_video.si(temp_dir, output_dir),
    #     # unsilence.si(temp_dir),
    #     cleanup_temp_directory.si(temp_dir, output_dir),
    # ).apply_async(
    #     # link_error=handle_error
    # )  # Link the tasks and handle errors


def handle_error(task_id, err, *args, **kwargs):
    print(f"Error in task {task_id}: {err}")
    # You can add additional error handling logic here
