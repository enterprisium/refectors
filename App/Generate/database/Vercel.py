import aiohttp, asyncio, pprint
from collections import deque


class AsyncImageGenerator:
    def __init__(self, session):
        self.session = session
        self.base = "https://auto-svg.vercel.app/"

    async def generate_image(self, payload, max_retries=50):
        retries = 0
        while retries < max_retries:
            try:
                url = f"{self.base}/predictions"
                data = {
                    "input": {
                        "width": 1024,
                        "height": 1024,
                        "prompt": payload,
                        "scheduler": "DPMSolver++",
                        "num_outputs": 1,
                        "guidance_scale": 2,
                        # "negative_prompt": "ugly, deformed, noisy, blurry, distorted, out of focus, bad anatomy, extra limbs, poorly drawn face, poorly drawn hands, missing fingers, color, 3D, 2D, video game, cgi, plastic, fake, artificial, smooth",
                        "negative_prompt": "text, watermark, blurry, haze, low contrast, low quality, underexposed, ugly, deformed, boring, bad quality, cartoon, ((disfigured)), ((bad art)), ((deformed)), ((poorly drawn)), ((extra limbs)), ((close up)), ((b&w)), weird colors, blurry, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, body out of frame, blurry, bad anatomy, blurred, watermark, grainy, signature, cut off, draft, low detail, low quality, double face, 2 faces, cropped, ugly, low-res, tiling, grainy, cropped, ostentatious, ugly, oversaturated, grain, low resolution, disfigured, blurry, bad anatomy, disfigured, poorly drawn face, mutant, mutated, extra limb, ugly, poorly drawn hands, missing limbs, blurred, floating limbs, disjointed limbs, deformed hands, blurred, out of focus, long neck, long body, ugly, disgusting, childish, cut off cropped, distorted, imperfect, surreal, bad hands, text, error, extra digit, fewer digits, cropped , worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, Lots of hands, extra limbs, extra fingers, conjoined fingers, deformed fingers, old, ugly eyes, imperfect eyes, skewed eyes , unnatural face, stiff face, stiff body, unbalanced body, unnatural body, lacking body, details are not clear, cluttered, details are sticky, details are low, distorted details, ugly hands, imperfect hands, (mutated hands and fingers:1.5), (long body :1.3), (mutation, poorly drawn :1.2) bad hands, fused ha nd, missing hand, disappearing arms, hands, disappearing thigh, disappearing calf, disappearing legs, ui, missing fingers",
                        "num_inference_steps": 25,
                    },
                    "path": "models/playgroundai/playground-v2.5-1024px-aesthetic/versions/a45f82a1382bed5c7aeb861dac7c7d191b0fdf74d8d57c4a0e6ed7d4d0bf7d24",
                }

                async with self.session.post(url, json=data) as response:
                    response.raise_for_status()
                    return await response.json()
            except aiohttp.ClientResponseError as e:
                if e.status == 500:
                    retries += 1
                    print(f"Retry {retries} after 500 error")
                    await asyncio.sleep(1)  # Add a delay before retrying
                else:
                    raise e

        # If max retries reached, raise an exception
        raise Exception("Max retries reached")

    async def fetch_image_status(self, image_id):
        url = f"https://replicate.com/api/predictions/{image_id}"
        async with self.session.get(url) as response:
            status = {}
            try:
                response.raise_for_status()
                temp = await response.json()
                status = temp
            except Exception as e:
                print(f"Image Request failed {e}")
                status["status"] = "404"

            while status["status"] != "succeeded":
                try:
                    status = await self._fetch_image_status(image_id)
                except Exception as e:
                    print(f"Image Request failed {e}")
                    pass
                await asyncio.sleep(3)
            return status

    async def _fetch_image_status(self, image_id):
        url = f"https://replicate.com/api/predictions/{image_id}"
        async with self.session.get(url) as response:
            response.raise_for_status()
            temp = await response.json()
            status = temp
            return status


async def process_images(payloads):
    async with aiohttp.ClientSession() as session:
        image_generator = AsyncImageGenerator(session)
        tasks = deque()
        results = []

        async def process_task():
            while tasks:
                payload = tasks.popleft()
                result = await image_generator.generate_image(payload)
                status = await image_generator.fetch_image_status(result["id"])
                print(status["output"])
                results.extend(status["output"])

        for payload in payloads:
            tasks.append(payload)
            if len(tasks) >= 2:
                await asyncio.gather(*[process_task() for _ in range(2)])

        # Process remaining tasks
        await asyncio.gather(*[process_task() for _ in range(len(tasks))])

        return results


# # Example payloads
# payloads = [
#     """
# Roman gladiator fighting a crocodile in the Colosseum, ancient Roman entertainment, oil painting, gruesome and thrilling, blood-stained sand, telephoto lens, afternoon golden hour lighting, cinematic film style, realistic with dramatic shadows
# """
# ]


# # Run the asyncio event loop
# async def main():
#     results = await process_images(payloads)
#     pprint.pprint(results)


# asyncio.run(main())
