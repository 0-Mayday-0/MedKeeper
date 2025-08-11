
from dotenv import load_dotenv
from os import getenv
from pymongo import MongoClient
from asyncio import run, create_task, to_thread
from asyncio import Task
from collections.abc import Coroutine
import strings as s

class ConnectionString:
    def __init__(self, env_path: str) -> None:
        load_dotenv(env_path)
        self.protocol: str = s.Connections.protocol
        self.user: str = getenv(s.Connections.username).lower()
        self.password: str = getenv(s.Connections.password)
        self.cluster: str = getenv(s.Connections.cluster)
        self.cluster_id: str = getenv(s.Connections.cluster_id)
        self.db: str = getenv(s.Connections.database)
        self.root_domain: str = s.Connections.root_domain
        self.top_domain: str = s.Connections.top_domain

    def __str__(self) -> str:
        return (f"{self.protocol}://{self.user}:"
                f"{self.password}@{self.cluster}."
                f"{self.cluster_id}.{self.root_domain}."
                f"{self.top_domain}/{self.db}")

class ClientCreator:
    def __init__(self, env_path: str):
        self.connection_string: ConnectionString = ConnectionString(env_path=env_path)

    async def connect_db(self) -> Coroutine[None, MongoClient[str], MongoClient]:

        client: Coroutine[None, MongoClient[str], MongoClient] = await to_thread(MongoClient, str(self.connection_string))

        return client


async def main() -> None:
    client_obj = ClientCreator(env_path=s.Paths.environment_path)

    client_task: Task[Coroutine[None, MongoClient[str], MongoClient]] = create_task(client_obj.connect_db())

    client_status: Coroutine[None, MongoClient[str], MongoClient] = await client_task

    print(client_status)

if __name__ == "__main__":
    run(main())