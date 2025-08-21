
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv

from pymongo.results import InsertOneResult
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database
from pymongo.cursor import Cursor

import strings as s
from connections import ClientCreator
from collections.abc import Coroutine, Callable
from asyncio import Task, create_task, run
from icecream import ic
from decimal import InvalidOperation, Decimal
from subprocess import call as spcall
from bson.objectid import ObjectId

from medobj import Medication


class Menu:
    def __init__(self, env_path: str) -> None:
        load_dotenv(env_path)

        self.columns_print: int = 3

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
            s.Menu.Internal.display_meds: self._display_all,
            s.Menu.Internal.quit_program: quit
        }

        self.commands_strings: list[str] = [s.Menu.Internal.add_string,
                                            s.Menu.Internal.remove_string,
                                            s.Menu.Internal.edit_medication_string,
                                            s.Menu.Internal.subtract_string,
                                            s.Menu.Internal.add_stock_string,
                                            s.Menu.Internal.edit_string,
                                            s.Menu.Internal.display_meds_string,
                                            s.Menu.Internal.quit_string
                                            ]

        self.client: MongoClient | None = None

        self.db: Database | None = None

        self.collection: Collection | None = None

        self.connected: bool = bool(self.client)

    @staticmethod
    def clear_screen() -> None:
        spcall(s.Menu.Internal.clear_command)

    @staticmethod
    def _check_valid_add(packed: dict[str, str]) -> Medication | None:
        try:
            assert packed[s.Connections.name_str].isalpha()
            packed[s.Connections.name_str] = packed[s.Connections.name_str].title()
        except AssertionError:
            print(s.Menu.External.ONLY_LETTERS, end='\n\n')
            return None

        try:
            med_object: Medication = Medication(None, *packed.values())
            ic(med_object)
        except InvalidOperation:
            return None

        return med_object

    def _avoid_duplicate(self, med: Medication) -> bool:
        strengths: list[dict[str, str | int]] = (self.collection.find( {s.Connections.name_str: med.get_name,
                                                                       s.Connections.strength_str: float(med.get_strength)} )
                                                 .to_list())

        return bool(strengths)

    def _check_exists(self, medication_name: str) -> bool:
        exists: list[dict[str, str | int]] | None = self.collection.find( {s.Connections.name_str: medication_name} ).to_list()
        meds: list[Medication] = [Medication(*doc.values()) for doc in exists]
        allowed_inputs: tuple[str, str] = s.Menu.Internal.yn_inputs
        user_input: str = ""
        user_invalid: bool = True

        if not exists:
            self.clear_screen()
            return True

        while exists and user_invalid:
            print(s.Menu.External.exists, end='')

            for med in meds:
                print(f'{med.get_name}: {med.get_strength}{s.Menu.External.milligrams}\n'
                      f'{s.Menu.External.stock}{med.get_qty}', end='\n\n')

            user_input = input(s.Menu.External.exists_sure)
            user_invalid = user_input not in allowed_inputs

            if user_invalid:
                self.clear_screen()
                print(s.Menu.External.INVALID_INPUT)

        return bool(int(user_input))




    def _add_medication(self) -> None:
        self.clear_screen()
        prompts: tuple[str, str, str] = s.Menu.External.add_med_prompts

        user_packed: dict[str, str] = {s.Connections.name_str: '',
                                       s.Connections.strength_str: '',
                                       s.Connections.qty_str: ''}

        for prompt, key in zip(prompts, user_packed.keys()):
            user_packed[key] = input(prompt)

        med_object = self._check_valid_add(user_packed)

        if not med_object:
            self.clear_screen()
            print(s.Menu.External.INVALID_CHARACTERS, end='\n\n')
        else:
            user_accepts: bool = self._check_exists(med_object.get_name)

            duplicate: bool = self._avoid_duplicate(med_object)

            if duplicate:
                self.clear_screen()
                print(s.Menu.External.DUPLICATE_MED)
            elif not user_accepts:
                self.clear_screen()
                print(s.Menu.External.USER_CANCEL)
            else:
                self.clear_screen()
                insert_result: InsertOneResult = self.collection.insert_one(med_object.__dict__())

                print(f'{s.Menu.External.INSERTED_SUCCESS} {insert_result.inserted_id}', end='\n\n')

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

    def _display_all(self):
        meds_with_id: list[dict[str, str | int]] = self.collection.find().to_list()
        self.clear_screen()

        meds: list[Medication] = [Medication(*doc.values()) for doc in meds_with_id]

        for index, med in enumerate(meds):
            print(f'{med.get_name}: {med.get_strength}{s.Menu.External.milligrams} {s.Menu.External.stock}{med.get_qty}', end=' '*4)
            if index % self.columns_print == self.columns_print -1:
                print('\n')


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
            while user_input != s.Menu.Internal.quit_program:
                for k, v in zip(self.commands.keys(), self.commands_strings):
                    print(f'{k.upper()}: {v}')
                user_input = input(f'\n{s.Menu.External.command_prompt}').lower()

                try:
                    ic(self.commands[user_input]())

                except NotImplementedError as e:
                    self.clear_screen()
                    print(f'{s.Menu.External.NOT_IMPLEMENTED}:\n{str(e)}', end='\n\n')

                except KeyError:
                    self.clear_screen()
                    print(s.Menu.External.INVALID_INPUT, end='\n\n')

        else:
            raise ConnectionError(s.Menu.External.NOT_CONNECTED)



async def main():
    menu_object: Menu = Menu(s.Paths.environment_path)

    await menu_object.show_commands()


if __name__ == "__main__":
    run(main())