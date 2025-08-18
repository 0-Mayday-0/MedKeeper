from dataclasses import dataclass

@dataclass(frozen=True)
class Connections:
    protocol: str = 'mongodb+srv'
    root_domain: str = 'mongodb'
    top_domain: str = 'net'

    cluster: str = "CLUSTER"
    username: str = "USERNAME"
    password: str = "PASSWORD"
    cluster_id: str = "CLUSTER_ID"
    database: str = "DB"
    collection: str = "COLLECTION"

    name_str: str = 'name'
    strength_str: str = 'strength'
    qty_str: str = 'qty'

@dataclass(frozen=True)
class Menu:
    @dataclass(frozen=True)
    class Internal:


        add_medication: str = 'a'
        subtract_stock: str = 's'
        add_stock: str = 'p'
        edit_stock: str = 'e'
        remove_medication: str = 'r'
        edit_medication: str = 'c'
        quit_program: str = 'q'

        clear_command: str = 'cmd /c cls'

        add_string: str = "Add a medication"
        subtract_string: str = "Subtract from stock"
        add_stock_string: str = "Add to stock"
        edit_string: str = "Edit the stock of a medication"
        remove_string: str = "Remove a medication"
        edit_medication_string: str = "Edit the name of a medication"
        quit_string: str = "Quit"

    @dataclass(frozen=True)
    class External:
        command_prompt: str = "Command: "

        add_med_prompts: tuple[str, str, str] = ("Enter the name of the medication: ",
                                                "Enter the strength of the medication: ",
                                                "Enter the current stock: ")

        NOT_IMPLEMENTED: str = "Not currently implemented. Callback correct"
        INVALID_INPUT: str = "Invalid input, please try again."
        NOT_CONNECTED: str = "Something went wrong connecting to the DB."
        ONLY_LETTERS: str = "The name of the medication must only contain letters."
        INVALID_CHARACTERS: str = "One of the values entered has invalid characters."

        INSERTED_SUCCESS: str = "Inserted med with ID:"



@dataclass(frozen=True)
class Paths:
    environment_path: str = ".\\credentials\\creds.env"