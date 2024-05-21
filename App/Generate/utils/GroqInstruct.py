import os
import instructor
from groq import Groq

from pydantic import BaseModel, Field

from typing import List, Dict
from pydantic import BaseModel


class Scene(BaseModel):
    narration: str
    image_prompts: List[str]


class VideoOutput(BaseModel):
    scenes: List[Scene]


client = Groq(api_key="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")

# By default, the patch function will patch the ChatCompletion.create and ChatCompletion.create methods to support the response_model parameter
client = instructor.from_groq(client, mode=instructor.Mode.JSON)


# Now, we can use the response_model parameter using only a base model
# rather than having to use the OpenAISchema class


def chatbot(prompt):

    response: VideoOutput = client.chat.completions.create(
        model="llama3-70b-8192",
        # model="gemma-7b-it",
        # model="llama2-70b-4096",
        # model="llama3-70b-8192",
        max_tokens=5000,
        response_model=VideoOutput,
        # kwargs={
        #     # "temperature": 1,
        #     "max_tokens": 5000,
        #     # "top_p": 1,
        #     "stream": False,
        #     "stop": None,
        # },
        messages=[
            {
                "role": "system",
                "content": """Take a deep breath. You are an amazing story teller, you keep your audience engaged here is an example of one of your stories:
                Title : Why are Jews so rich
                 it starts in
medieval Europe the church and Islamic
law both prohibit money lending but not
Jews they loan money and interest makes
them very wealthy so wealthy that even
powerful monarchs borrow from them by
the 17th century they become key members
of Royal courts known as Court Jews
financial advisers to Kings and Queens
when the world transitioned from
monarchy to democracy Jewish people with
their centuries of experience were the
first to take advantage of new banking
infrastructures today however the world
is very different Muslims Christians
Jews everyone enjoys interest
                
                
                """,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )
    return response.dict()
