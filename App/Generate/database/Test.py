import aiohttp
import asyncio
import json
import random
import secrets


async def generate_with_playground(prompt, resolution):
    nevPrompt = "text, watermark, blurry, haze, low contrast, low quality, underexposed, ugly, deformed, boring, bad quality, cartoon, ((disfigured)), ((bad art)), ((deformed)), ((poorly drawn)), ((extra limbs)), ((close up)), ((b&w)), weird colors, blurry, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, body out of frame, blurry, bad anatomy, blurred, watermark, grainy, signature, cut off, draft, low detail, low quality, double face, 2 faces, cropped, ugly, low-res, tiling, grainy, cropped, ostentatious, ugly, oversaturated, grain, low resolution, disfigured, blurry, bad anatomy, disfigured, poorly drawn face, mutant, mutated, extra limb, ugly, poorly drawn hands, missing limbs, blurred, floating limbs, disjointed limbs, deformed hands, blurred, out of focus, long neck, long body, ugly, disgusting, childish, cut off cropped, distorted, imperfect, surreal, bad hands, text, error, extra digit, fewer digits, cropped , worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurry, artist name, Lots of hands, extra limbs, extra fingers, conjoined fingers, deformed fingers, old, ugly eyes, imperfect eyes, skewed eyes , unnatural face, stiff face, stiff body, unbalanced body, unnatural body, lacking body, details are not clear, cluttered, details are sticky, details are low, distorted details, ugly hands, imperfect hands, (mutated hands and fingers:1.5), (long body :1.3), (mutation, poorly drawn :1.2) bad hands, fused ha nd, missing hand, disappearing arms, hands, disappearing thigh, disappearing calf, disappearing legs, ui, missing fingers"
    width, height = None, None
    if resolution == "Square":
        width = 1024
        height = 1024
    elif resolution == "Wide":
        width = 1280
        height = 768
    elif resolution == "Portrait":
        width = 768
        height = 1280

    session_hash = generate_session_hash()
    random_digit = generate_random_digits()
    root_url = "https://playgroundai-playground-v2-5.hf.space/--replicas/bdj8s"

    url_join_queue = f"https://playgroundai-playground-v2-5.hf.space/queue/join?fn_index=3&session_hash={session_hash}"
    headers = {"Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        async with session.get(url_join_queue) as resp:
            async for line in resp.content:
                temp = line.decode().replace("data: ", "")
                print(temp, "here")
                try:
                    temp = eval(temp)
                except:
                    continue
                print(type(temp))
                data = temp
                if data["msg"] == "send_data":
                    event_id = data.get("event_id")
                    await session.post(
                        "https://playgroundai-playground-v2-5.hf.space/queue/data",
                        json={
                            "data": [
                                prompt,
                                nevPrompt,
                                True,
                                random_digit,
                                width,
                                height,
                                3,
                                True,
                            ],
                            "event_data": None,
                            "fn_index": 3,
                            "trigger_id": 6,
                            "session_hash": session_hash,
                            "event_id": event_id,
                        },
                    )
                elif data["msg"] == "process_completed":
                    image_paths = data["output"]["data"][0]
                    print(image_paths, "hererereere")
                    first_image_path = (
                        image_paths[0]["image"]["path"] if image_paths else None
                    )
                    if first_image_path:
                        print(first_image_path)
                        full_url = f"{root_url}/file={first_image_path}"
                        return {
                            "images": [{"url": full_url}],
                            "modelUsed": "Playground",
                        }
                    else:
                        raise ValueError(
                            "No image path found in the process_completed message."
                        )


async def fetch_and_extract_root_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.text()


def generate_session_hash():
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    return "".join(secrets.choice(chars) for _ in range(5))


def generate_random_digits():
    return random.randint(100000000, 999999999)


async def main():
    prompt = "COMICBOOK ILLUSTRATION Medea, Jason, two sons, black background, 8k"
    resolution = "Square"
    result = await generate_with_playground(prompt, resolution)
    print(result)


# Run the main function
asyncio.run(main())
