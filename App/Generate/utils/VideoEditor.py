from pydantic import BaseModel, Field, validator
from typing import List, Dict



transitions = [
    "WaveRight_transparent.webm",
    "WaveLeft_transparent.webm",
    "WaveBlue_transparent.webm",
    "Wave_transparent.webm",
    "Swirl_transparent.webm",
    "Snow_transparent.webm",
    "Likes_transparent.webm",
    "Lightning_transparent.webm",
    "Happy_transparent.webm",
    "Fire_transparent.webm",
    "CurlingWave_transparent.webm",
    "Cloud_transparent.webm",
]


class Asset(BaseModel):
    type: str
    sequence: List[Dict]

    @validator("sequence")
    def check_duration(cls, sequence):
        for item in sequence:
            start = item.get("start", 0)
            end = item.get("end", 0)
            duration = (end - start) * 30  # Assuming 30 fps
            if duration <= 1:
                raise ValueError("Asset duration must be greater than 1 frame.")
        return sequence


class Link(BaseModel):
    file_name: str
    link: str


class Remotion(BaseModel):
    links: List[Link] = []
    assets: List[Asset] = []
    constants: Dict[str, int] = {"duration": 3840, "height": 1920, "width": 1080}
    scenes: int
    total_duration: int

    def generate_image_links(self):
        for i in range(self.scenes):
            image_file_name = f"image_{i}.png"
            image_link = f"https://image.lexica.art/full_webp/{i}.png"
            self.links.append(Link(file_name=image_file_name, link=image_link))


def concatenate_wav_files(input):
    # Initialize variables for output file
    output = None
    output_params = None
    output_file =  ''
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
                    if input_wav.getparams() != output_params:
                        raise ValueError(
                            "Input file parameters do not match output file parameters."
                        )

                # Read data from input file and write to output file
                output.writeframes(input_wav.readframes(input_wav.getnframes()))
    finally:
        # Close output file
        if output is not None:
            output.close()


# # Example usage
# input_files = ["file1.wav", "file2.wav", "file3.wav"]
# output_file = "output.wav"
# concatenate_wav_files(input_files, output_file)
