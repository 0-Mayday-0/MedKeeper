
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database

import strings as s
from connections import ClientCreator
from collections.abc import Coroutine, Callable
from asyncio import Task, create_task, run
from icecream import ic


class Menu:
    def __init__(self, env_path: str) -> None:
        load_dotenv(env_path)

        self.env_path = env_path
        self.cluster: str = getenv(s.Connections.cluster)
        self.database: str = getenv(s.Connections.database)
        self.col: str = getenv(s.Connections.collection)

        self.commands: dict[str, Callable] = {
            s.Menu.Internal.add_medication: self._add_medication,
            s.Menu.Internal.remove_medication: self._remove_medication,
            s.Menu.Internal.edit_medication: self._edit_medication,
            s.Menu.Internal.subtract_stock: self._subtract_stock,
            s.Menu.Internal.add_stock: self._add_stock,
            s.Menu.Internal.edit_stock: self._edit_stock,
            s.Menu.Internal.quit_program: quit
        }

        self.commands_strings: list[str] = [s.Menu.Internal.add_string,
                                            s.Menu.Internal.remove_string,
                                            s.Menu.Internal.edit_medication_string,
                                            s.Menu.Internal.subtract_string,
                                            s.Menu.Internal.add_stock_string,
                                            s.Menu.Internal.edit_string,
                                            s.Menu.Internal.quit_string
                                            ]

        self.client: MongoClient | None = None

        self.db: Database | None = None

        self.collection: Collection | None = None

        self.connected: bool = bool(self.client)

    def _add_medication(self):
        raise NotImplementedError(s.Menu.Internal.add_medication)

    def _subtract_stock(self):
        raise NotImplementedError(s.Menu.Internal.subtract_string)

    def _add_stock(self):
        raise NotImplementedError(s.Menu.Internal.add_stock_string)

    def _edit_stock(self):
        raise NotImplementedError(s.Menu.Internal.edit_string)

    def _remove_medication(self):
        raise NotImplementedError(s.Menu.Internal.remove_string)

    def _edit_medication(self):
        raise NotImplementedError(s.Menu.Internal.edit_medication_string)

    async def _connect(self) -> Coroutine[None, MongoClient[str], MongoClient]:
        client_object: ClientCreator = ClientCreator(self.env_path)

        client_task: Task[Coroutine[None, MongoClient[str], MongoClient]] = create_task(client_object.connect_db())

        client_status: Coroutine[None, MongoClient[str], MongoClient] = await client_task

        return client_status

    async def _check_connected(self) -> None:
        self.connected: bool = bool(self.client)
        if self.connected:
            pass
        else:
            awaitable_connect: Coroutine[None, MongoClient[str], MongoClient] = await self._connect()
            self.client: Coroutine[None, MongoClient[str], MongoClient] = awaitable_connect
            self.connected = bool(self.client)

            self.db = self.client[self.database]
            self.collection = self.db[self.col]



    async def show_commands(self) -> None:
        await self._check_connected()
        user_input: str = ''

        if self.connected:
            while user_input != 'q':
                for k, v in zip(self.commands.keys(), self.commands_strings):
                    print(f'{k.upper()}: {v}')
                user_input = input(f'\n{s.Menu.External.command_prompt}').lower()

                try:
                    ic(self.commands[user_input]())

                except NotImplementedError as e:
                    print(f'{s.Menu.External.NOT_IMPLEMENTED}:\n{str(e)}', end='\n\n')

                except KeyError:
                    print(s.Menu.External.INVALID_INPUT, end='\n\n')
        else:
            raise ConnectionError(s.Menu.External.NOT_CONNECTED)



async def main():
    menu_object: Menu = Menu(s.Paths.environment_path)

    await menu_object.show_commands()


if __name__ == "__main__":
    run(main())