import asyncio
import aiohttp
import os, uuid
from collections import deque
import wave
import uuid
from pydub import AudioSegment


import wave
import struct


def concatenate_wave_files(input_file_paths, output_file_path):
    """
    Concatenates multiple wave files and saves the result to a new file.

    :param input_file_paths: A list of paths to the input wave files.
    :param output_file_path: The path to the output wave file.
    """
    # Check if input file paths are provided
    if not input_file_paths:
        raise ValueError("No input file paths provided.")

    # Validate output file path
    if not output_file_path:
        raise ValueError("Output file path is empty.")

    # Validate input file paths
    for input_file_path in input_file_paths:
        if not input_file_path:
            raise ValueError("Empty input file path found.")

    # Validate and get parameters from the first input file
    with wave.open(input_file_paths[0], "rb") as input_file:
        n_channels = input_file.getnchannels()
        sampwidth = input_file.getsampwidth()
        framerate = input_file.getframerate()
        comptype = input_file.getcomptype()
        compname = input_file.getcompname()

    # Open the output file for writing
    output_file = wave.open(output_file_path, "wb")
    output_file.setnchannels(n_channels)
    output_file.setsampwidth(sampwidth)
    output_file.setframerate(framerate)
    output_file.setcomptype(comptype, compname)

    # Concatenate and write data from all input files to the output file
    for input_file_path in input_file_paths:
        with wave.open(input_file_path, "rb") as input_file:
            output_file.writeframes(input_file.readframes(input_file.getnframes()))

    # Close the output file
    output_file.close()

    print(
        f"Successfully concatenated {len(input_file_paths)} files into {output_file_path}"
    )


# # Example usage
# input_files = ["./tmp/" + i for i in os.listdir("./tmp")]
# output_file = "./concatenated_output.wav"
# concatenate_wave_files(input_files, output_file)


def concatenate_wav_files(input_files, file_directory):
    print(input_files)
    output_file = file_directory + str(uuid.uuid4()) + "final.wav"
    # Initialize variables for output file
    output = None
    output_params = None

    try:
        # Open output file for writing
        output = wave.open(output_file, "wb")

        # Loop through input files
        for input_file in input_files:
            with wave.open(input_file, "rb") as input_wav:
                # If this is the first input file, set output file parameters
                if output_params is None:
                    output_params = input_wav.getparams()
                    output.setparams(output_params)
                # Otherwise, ensure consistency of parameters
                else:
                    pass
                    # if input_wav.getparams() != output_params:
                    #     raise ValueError(
                    #         "Input file parameters do not match output file parameters."
                    #     )

                # Read data from input file and write to output file
                output.writeframes(input_wav.readframes(input_wav.getnframes()))
    finally:
        # Close output file
        if output is not None:
            output.close()
    return (output_file,)


class Speak:
    def __init__(self, api_url="https://yakova-embedding.hf.space", dir="./tmp"):
        self.api_url = api_url
        self.dir = dir

    async def _make_transcript(self, links, text):
        data = {"audio_url": links, "text": text}
        response_data = await self._make_request(
            "post", "descript_transcript", json=data
        )
        return response_data

    async def _make_request(self, method, endpoint, json=None):
        async with aiohttp.ClientSession() as session:
            async with getattr(session, method)(
                f"{self.api_url}/{endpoint}", json=json
            ) as response:
                return await response.json()

    async def say(self, text, speaker="Tabitha"):
        data = {"text": text, "speaker": speaker}

        response_data = await self._make_request("post", "descript_tts", json=data)
        tts_id = response_data["id"]

        # Poll the status endpoint until the TTS is ready
        while True:
            status_data = await self._make_request(
                "post", "descript_status", json={"id": tts_id}
            )
            print(status_data)
            if "status" in status_data:
                if status_data["status"] == "done":
                    audio_url = status_data["url"]
                    temp = await self.download_file(audio_url)
                    return audio_url, temp
            else:
                pass

            await asyncio.sleep(1)

    async def download_file(self, url):
        filename = str(uuid.uuid4()) + ".wav"
        os.makedirs(self.dir, exist_ok=True)
        save_path = os.path.join(self.dir, filename)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    with open(save_path, "wb") as file:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            file.write(chunk)

        return save_path


async def process_narrations(narrations):
    speak = Speak()
    tasks = deque()
    results = []
    files = []

    async def process_task():
        while tasks:
            text = tasks.popleft()
            result = await speak.say(text)
            _, temp = result
            results.append(result)
            files.append(temp)

    for narration in narrations:
        tasks.append(narration)
        if len(tasks) >= 2:
            await asyncio.gather(*[process_task() for _ in range(2)])

    # Process remaining tasks
    await asyncio.gather(*[process_task() for _ in range(len(tasks))])
    concatinated_file = concatenate_wav_files(files, speak.dir)

    wav_file = AudioSegment.from_file(concatinated_file, format="wav")
    duration_in_seconds = int(len(wav_file) / 1000)

    return results, (concatinated_file, duration_in_seconds)


# # Example narrations
# narrations = [
#     "Welcome to a journey through some of history's strangest moments!",
#     "Did you know that in ancient Rome, mustaches were a big deal?",
# ]


# # Run the asyncio event loop
# async def main():
#     results = await process_narrations(narrations)
#     print("Results:", results)


# asyncio.run(main())
