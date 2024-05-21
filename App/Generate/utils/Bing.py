import aiohttp
import json
import re


class Bing:
    def __init__(self):
        self.url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": "Bearer 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",
            "accept": "application/json",
            "content-type": "application/json",
        }

    @staticmethod
    def remove_links(text):
        # Remove links
        cleaned_text = re.sub(r"\[\d+\]:\shttps?://\S+\s?\"\"", "", text)

        # Remove other weird characters
        # cleaned_text = re.sub(r'[^a-zA-Z0-9\s.,?!-]', '', cleaned_text)

        return cleaned_text

    async def chat(self, message, remove_links=False, content=False):
        messages = [
            {"role": "user", "content": message},
            {"role": "assistant", "content": "You are an amazing Youtuber"},
            # Add more messages as needed
        ]

        payload = {
            "messages": messages,
            "stream": False,
            "model": "mixtral-8x7b-32768",
            "temperature": 0.5,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "top_p": 1,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url, headers=self.headers, data=json.dumps(payload)
            ) as response:
                result = await response.json()
                # print(result)
                # result = json.loads(result)
                assistant_message_content = result["choices"][0]["message"]["content"]
                # print(assistant_message_content)
                if remove_links:
                    return self.remove_links(assistant_message_content)
                return assistant_message_content
