from pyrogram import Client
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from typing import List, Optional, Dict
import os
import aiohttp
from pydantic import BaseModel


class Node(BaseModel):
    MASTER: bool
    SPACE_HOST: str


class NodeTaskState(BaseModel):
    NODE: Node
    CHUNK: int
    COMPLETED: bool


class Task(BaseModel):
    TASK_ID: str
    COMPLETED: bool = False
    NODES: Optional[List[NodeTaskState]] = []

    def is_completed(self) -> bool:
        for node in self.NODES:
            if not node.COMPLETED:
                return False
        self.COMPLETED = True
        return True

    def mark_node_completed(self, space_host: str):
        for state in self.NODES:
            if state.NODE.SPACE_HOST == space_host:
                state.COMPLETED = True
                break

    async def add_node(self, node: Node, CHUNK: int):
        new_node_state = NodeTaskState(NODE=node, CHUNK=CHUNK, COMPLETED=False)
        self.NODES.append(new_node_state)

    @classmethod
    async def _check_node_online(cls, space_host: str) -> bool:
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=5)
            ) as session:
                async with session.get(space_host) as response:
                    return response.status == 200
        except aiohttp.ClientError:
            return False


class ServerState(Node):
    CACHED: bool
    TASKS: Optional[Dict[str, Task]] = {}
    NODES: Optional[list[Node]]
    DB: str = "https://herokuserver-185316.firebaseio.com/"

    def get_master(self) -> Optional[Node]:
        for node in self.NODES:
            if node.NODE.MASTER:
                return node.NODE
        return None


TELEGRAM_SESSION = os.environ.get("TELEGRAM_SESSION", "RANDOM_STRING")
TELEGRAM_SESSION_PYROGRAM = os.environ.get("TELEGRAM_SESSION_PYROGRAM", " ")
MASTER_SERVER = bool(os.environ.get("MASTER", 0))
SPACE_HOST = os.environ.get("SPACE_HOST", "RANDOM_STRING")


SERVER_STATE = ServerState(
    CACHED=False, MASTER=MASTER_SERVER, SPACE_HOST=SPACE_HOST, NODES=None
)


bot: TelegramClient = TelegramClient(
    StringSession(TELEGRAM_SESSION),
    api_id=870972,
    api_hash="ce2efaca02dfcd110941be6025e9ac0d",
)


# bot: Client = Client("mboneabot", session_string=TELEGRAM_SESSION_PYROGRAM, workers=5 ,workdir="/srv")
