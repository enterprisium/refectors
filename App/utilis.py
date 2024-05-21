import aiohttp, asyncio
from App import SERVER_STATE, Node

import aiohttp


async def upload_file(file_path: str, node: str, chunk: int, task: str):
    master_node = SERVER_STATE.get_master()
    url = f"http://{master_node.SPACE_HOST}/uploadfile/?node={node}&chunk={chunk}&task={task}"
    async with aiohttp.ClientSession() as session:
        headers = {"Transfer-Encoding": "chunked"}
        with open(file_path, "rb") as file:
            async with session.post(url, headers=headers, data=file) as response:
                if response.status == 200:
                    print("File uploaded successfully")
                else:
                    print("Failed to upload file")


class WorkerClient:
    base_url = SERVER_STATE.DB

    async def register_worker(self):
        async with aiohttp.ClientSession() as session:
            data = {
                "WORKER_ID": SERVER_STATE.SPACE_HOST,
                "MASTER": SERVER_STATE.MASTER,
                "HOST_NAME": SERVER_STATE.SPACE_HOST,
                "SPACE_HOST": SERVER_STATE.SPACE_HOST,
            }
            response = await self.get_node()
            if response:
                return response

            async with session.put(
                f"{self.base_url}/nodes/{SERVER_STATE.SPACE_HOST}.json", json=data
            ) as resp:
                return await resp.json()

    async def get_node(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base_url}/nodes/{SERVER_STATE.SPACE_HOST}.json"
            ) as resp:
                response = await resp.json()
                return response

    async def delete_node(self):
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                f"{self.base_url}/nodes/{SERVER_STATE.SPACE_HOST}.json"
            ) as resp:
                response = await resp.json()

    async def get_all_nodes(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/nodes.json") as resp:
                response = await resp.json()
                SERVER_STATE.NODES = [Node(**value) for value in response.values()]
                return SERVER_STATE.NODES
