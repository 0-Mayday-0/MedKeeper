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
        display_meds: str = 'd'
        quit_program: str = 'q'

        id_header: str = '_id'

        yn_inputs: tuple[str, str] = ('0', '1')

        clear_command: str = 'cmd /c cls'

        add_string: str = "Add a medication"
        subtract_string: str = "Subtract from stock"
        add_stock_string: str = "Add to stock"
        edit_string: str = "Edit the stock of a medication"
        remove_string: str = "Remove a medication"
        edit_medication_string: str = "Edit the name of a medication"
        display_meds_string: str = "Display all medications and their stock"
        quit_string: str = "Quit"

    @dataclass(frozen=True)
    class External:
        command_prompt: str = "Command: "
        milligrams: str = 'mg'
        stock: str = "Stock: "

        add_med_prompts: tuple[str, str, str] = ("Enter the name of the medication: ",
                                                "Enter the strength of the medication: ",
                                                "Enter the current stock: ")

        exists: str = "Medication with this name already exists as:\n\n"
        exists_sure: str = "Are you sure you want to add a different strength? [0/1]: "

        NOT_IMPLEMENTED: str = "Not currently implemented. Callback correct"
        INVALID_INPUT: str = "Invalid input, please try again."
        NOT_CONNECTED: str = "Something went wrong connecting to the DB."
        ONLY_LETTERS: str = "The name of the medication must only contain letters."
        INVALID_CHARACTERS: str = "One of the values entered has invalid characters."
        USER_CANCEL: str = "Operation cancelled by user, med insertion failed."
        DUPLICATE_MED: str = "A medication with this strength already exists, duplicates are not allowed. Med insertion failed."
        INSERTED_SUCCESS: str = "Inserted med with ID:"
        HANDSHAKE_FAILED: str = "Your IP is not allowed to make changes in the DB. Please contact the system administrator."


@dataclass(frozen=True)
class Paths:
    environment_path: str = ".\\credentials\\creds.env"