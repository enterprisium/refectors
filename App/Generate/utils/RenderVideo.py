import aiohttp, json


class RenderVideo:
    def __init__(self, url="https://yakova-rectifier.hf.space/create-video"):
        self.url = url

    @staticmethod
    def _parse_response(response: str) -> dict:
        return json.loads(response)

    async def post_request(self, data: dict) -> dict:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url, data=json.dumps(data), headers=headers
            ) as resp:
                response = await resp.text()
                result = self._parse_response(response)
        return result

    async def render_video(self, data) -> dict:
        result = await self.post_request(data)
        return result
