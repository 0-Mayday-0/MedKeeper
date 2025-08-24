
from pymongo import MongoClient
from dotenv import load_dotenv
from os import getenv
import re

from pymongo.results import InsertOneResult, DeleteResult, UpdateResult
from pymongo.synchronous.collection import Collection
from pymongo.synchronous.database import Database
from pymongo.errors import ServerSelectionTimeoutError
from pymongo.cursor import Cursor

import strings as s
from connections import ClientCreator
from collections.abc import Coroutine, Callable, Mapping
from asyncio import Task, create_task, run
from icecream import ic
from decimal import InvalidOperation, Decimal, getcontext
from subprocess import call as spcall



from medobj import Medication


class Menu:
    def __init__(self, env_path: str) -> None:
        load_dotenv(env_path)

        self.columns_print: int = 3 #the amount of columns for printing available meds
        self.spacing: int = 4 #the spacing between columns
        self.ndigits: int = 2 #amount of decimal digits for Decimal() objects

        getcontext().prec = self.ndigits #set context for Decimal()

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
            s.Menu.Internal.find_name: self._find_name,
            s.Menu.Internal.quit_program: quit
        }

        self.commands_strings: list[str] = [s.Menu.Internal.add_string,
                                            s.Menu.Internal.remove_string,
                                            s.Menu.Internal.edit_medication_string,
                                            s.Menu.Internal.subtract_string,
                                            s.Menu.Internal.add_stock_string,
                                            s.Menu.Internal.edit_string,
                                            s.Menu.Internal.display_meds_string,
                                            s.Menu.Internal.find_name_string,
                                            s.Menu.Internal.quit_string
                                            ]

        self.client: MongoClient | None = None

        self.db: Database | None = None

        self.collection: Collection | None = None

        self.connected: bool = bool(self.client)

    def _get_all_med_docs(self) -> list[Mapping[str, str | int]]:
        return self.collection.find().to_list()

    def _get_all_med_objects(self) -> list[Medication]:
        return [Medication(*doc.values()) for doc in self._get_all_med_docs()]


    @staticmethod
    def clear_screen() -> None:
        spcall(s.Menu.Internal.clear_command)

    @staticmethod
    def _check_valid_add(packed: dict[str, str]) -> Medication | None:
        try:
            assert packed[s.Connections.name_str].replace(' ', '').isalpha()
            packed[s.Connections.name_str] = packed[s.Connections.name_str].title()
        except AssertionError:
            print(s.Menu.External.ONLY_LETTERS, end='\n\n')
            return None

        try:
            med_object: Medication = Medication(None, *packed.values())
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

    @staticmethod
    def _check_valid_find_name(partial_name) -> bool:
        try:
            assert partial_name.replace(' ', '').isalpha(), bool(partial_name)
            return True

        except AssertionError:
            return False

    def _find_name(self) -> None:
        user_invalid: bool = True
        partial_name: str = ''
        matched: Cursor | None = None

        while user_invalid:
            partial_name = input(s.Menu.External.find_name)
            re_match: str = f".*({partial_name}).*"
            user_invalid = not self._check_valid_find_name(partial_name)

            if user_invalid:
                self.clear_screen()
                print(s.Menu.External.ONLY_LETTERS, end='\n\n')

            else:
                matched: Cursor = self.collection.find({s.Connections.name_str: re.compile(re_match, flags=re.IGNORECASE)})

                matched: list[Medication] = [Medication(*doc.values()) for doc in matched]

        self.clear_screen()
        print(s.Menu.External.found_these.format(m=partial_name), end='\n\n')



        for index, med in enumerate(matched):
            print(f'{str(med)}', end=' '*self.spacing)

            if index % self.columns_print == self.columns_print-1:
                print(flush=True)
        print('\n', flush=True)


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
        user_invalid: bool = True
        user_input: str = ''
        found_meds: list[Medication] | list[None] = []

        self.clear_screen()

        while user_invalid and not found_meds:

            user_input = input(s.Menu.External.prompt_subtract)

            user_invalid = not self._check_valid_name(user_input)

            if user_invalid:
                self.clear_screen()
                print(s.Menu.External.ONLY_LETTERS, end='\n\n')

            else:
                found_meds = self._find_remove(user_input.title())


        if not found_meds:
            self.clear_screen()
            print(s.Menu.External.NO_MEDS.format(m=user_input), end='\n\n')

        else:
            med_name: str = user_input
            user_invalid = True

        selected: Medication | None = None

        while user_invalid and found_meds:
            print(s.Menu.External.found_these.format(m=med_name), end='\n\n')

            for med in found_meds:
                print(f'{str(med)}')

            print()

            user_input = input(s.Menu.External.select_one_subtract)

            user_input: Decimal | None = self._check_valid_strength(user_input)

            user_invalid = not bool(user_input)

            if user_invalid:
                self.clear_screen()
                print(s.Menu.External.ONLY_NUMBERS, end='\n\n')
            else:
                for med in found_meds:
                    if user_input == med.get_strength:
                        selected = med

            if not selected:
                self.clear_screen()
                print(s.Menu.External.NO_SUCH_STRENGTH)

        user_invalid = True

        while user_invalid and selected:
            user_input: str = input(s.Menu.External.subtract_how_many)

            user_input: Decimal | None = self._check_valid_strength(user_input) #rename this function, checks if valid decimal

            user_invalid = not bool(user_input)

            if user_invalid:
                self.clear_screen()
                print(s.Menu.External.ONLY_NUMBERS, end='\n\n')

            else:
                user_invalid = user_input > selected.get_qty

                if user_invalid:
                    self.clear_screen()
                    print(s.Menu.External.STOCK_OVERLOAD.format(p=user_input,
                                                                m=selected.get_qty))

                else:
                    update_values: dict[str, dict[str, float]] = {s.Atomic.increment: {s.Connections.qty_str: float(-user_input)}}

                    update_result: UpdateResult = self.collection.update_one(filter=selected.__dict__(), update=update_values)

                    self.clear_screen()

                    print(s.Menu.External.SUBTRACT_SUCCESS.format(p=user_input,
                                                                  m=selected.get_name,
                                                                  i=selected.get_id),
                          f'Ack={update_result.acknowledged}',end='\n\n')




    def _add_stock(self):
        user_invalid: bool = True
        user_input: str = ''
        found_meds: list[Medication] | list[None] = []

        self.clear_screen()

        while user_invalid and not found_meds:

            user_input = input(s.Menu.External.prompt_add_stock)

            user_invalid = not self._check_valid_name(user_input)

            if user_invalid:
                self.clear_screen()
                print(s.Menu.External.ONLY_LETTERS, end='\n\n')

            else:
                found_meds = self._find_remove(user_input.title())

        if not found_meds:
            self.clear_screen()
            print(s.Menu.External.NO_MEDS.format(m=user_input), end='\n\n')

        else:
            med_name: str = user_input
            user_invalid = True

        selected: Medication | None = None

        while user_invalid and found_meds:
            print(s.Menu.External.found_these.format(m=med_name), end='\n\n')

            for med in found_meds:
                print(f'{str(med)}')

            print()

            user_input = input(s.Menu.External.select_one_add)

            user_input: Decimal | None = self._check_valid_strength(user_input)

            user_invalid = not bool(user_input)

            if user_invalid:
                self.clear_screen()
                print(s.Menu.External.ONLY_NUMBERS, end='\n\n')
            else:
                for med in found_meds:
                    if user_input == med.get_strength:
                        selected = med

            if not selected:
                self.clear_screen()
                print(s.Menu.External.NO_SUCH_STRENGTH)

        user_invalid = True

        while user_invalid and selected:
            user_input: str = input(s.Menu.External.add_how_many)

            user_input: Decimal | None = self._check_valid_strength(
                user_input)  # rename this function, checks if valid decimal

            user_invalid = not bool(user_input)

            if user_invalid:
                self.clear_screen()
                print(s.Menu.External.ONLY_NUMBERS, end='\n\n')

            else:
                update_values: dict[str, dict[str, float]] = {
                    s.Atomic.increment: {s.Connections.qty_str: float(user_input)}}

                update_result: UpdateResult = self.collection.update_one(filter=selected.__dict__(),
                                                                         update=update_values)

                self.clear_screen()

                print(s.Menu.External.ADD_SUCCESS.format(p=user_input,
                                                         m=selected.get_name,
                                                         i=selected.get_id),
                      f'Ack={update_result.acknowledged}', end='\n\n')

    def _edit_stock(self):
        raise NotImplementedError(s.Menu.Internal.edit_string)


    @staticmethod
    def _check_valid_name(medication_name: str) -> bool:
        try:
            assert medication_name.replace(' ', '').lower().isalpha(), bool(medication_name)
            return True
        except AssertionError:
            return False

    def _find_remove(self, medication_name) -> list[Medication] | list[None]:
        found_docs: list[Mapping[str, str | int]] = self.collection.find( {s.Connections.name_str: medication_name.title()} ).to_list()

        return [Medication(*doc.values()) for doc in found_docs]

    @staticmethod
    def _check_valid_strength(strength: str) -> Decimal | None:
        try:
            assert bool(strength)
            return Decimal(strength)

        except AssertionError:
            print(s.Menu.External.STRENGTH_NOT_EMPTY, end='\n\n')

        except InvalidOperation:
            print(s.Menu.External.ONLY_NUMBERS, end='\n\n')

    def _remove_medication(self):
        user_invalid: bool = True
        user_input: str = ''
        med_name: str = ''

        while user_invalid:
            self.clear_screen()
            user_input = input(s.Menu.External.remove_med_prompt)
            user_invalid = not self._check_valid_name(user_input)

            if user_invalid:
                print(s.Menu.External.NOT_EMPTY_OR_SPECIAL, end='\n\n')

            else:
                self.clear_screen()
                break

        user_invalid: bool = True
        meds_found: list[Medication] | list[None] = self._find_remove(user_input)
        to_remove: Medication | None = None

        med_name = user_input

        while user_invalid and meds_found:
            print(s.Menu.External.found_these.format(m=med_name), end='\n\n')

            for med in meds_found:
                print(f'{str(med)}')

            user_input = input(f'\n{s.Menu.External.select_one_remove}')
            user_input: Decimal | None = self._check_valid_strength(user_input)
            user_invalid = not bool(user_input)

            try:
                for med in meds_found:
                    if not med.get_strength == user_input:
                        continue
                    else:
                        to_remove = med
                assert to_remove

            except AssertionError:
                self.clear_screen()
                user_invalid = True
                print(s.Menu.External.NO_SUCH_STRENGTH, end='\n\n')

        if not meds_found:
            print(s.Menu.External.NO_MEDS.format(m=user_input), end='\n\n')


        allowed_inputs: tuple[str, str] = s.Menu.Internal.yn_inputs
        user_invalid = True

        while user_invalid and meds_found:
            user_input = input(s.Menu.External.remove_sure.format(m=to_remove.get_name,
                                                                  s=to_remove.get_strength))

            user_invalid = not user_input in allowed_inputs

            if user_invalid:
                print(s.Menu.External.INVALID_INPUT)

        if meds_found:
            user_input: bool = bool(int(user_input))
            self.clear_screen()
            if user_input:
                del_result: DeleteResult = self.collection.delete_one( to_remove.__dict__() )
                print(s.Menu.External.REMOVE_SUCCESS, to_remove.get_id, f'Ack={del_result.acknowledged}', end='\n\n')
            else:
                print(s.Menu.External.USER_CANCEL, end='\n\n')

    def _edit_medication(self):
        raise NotImplementedError(s.Menu.Internal.edit_medication_string)

    def _display_all(self):
        self.clear_screen()

        meds: list[Medication] = self._get_all_med_objects()

        for index, med in enumerate(meds):
            print(f'{str(med)}', end=' '*self.spacing)
            if index % self.columns_print == self.columns_print -1:
                print(flush=True)
        print('\n', flush=True)


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

                except ServerSelectionTimeoutError:
                    self.clear_screen()
                    print(s.Menu.External.HANDSHAKE_FAILED)

        else:
            raise ConnectionError(s.Menu.External.NOT_CONNECTED)



async def main():
    menu_object: Menu = Menu(s.Paths.environment_path)

    await menu_object.show_commands()


if __name__ == "__main__":
    run(main())