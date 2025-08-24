from dataclasses import dataclass

@dataclass(frozen=True)
class Atomic:
    increment: str = '$inc'
    set: str = '$set'

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
        find_name: str = "f"
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
        find_name_string: str = "Find a medication by name"
        quit_string: str = "Quit"

    @dataclass(frozen=True)
    class External:
        command_prompt: str = "Command: "
        milligrams: str = 'mg'
        stock: str = "Stock: "

        add_med_prompts: tuple[str, str, str] = ("Enter the name of the medication: ",
                                                "Enter the strength of the medication: ",
                                                "Enter the current stock: ")

        remove_med_prompt: str = "Enter the full name of the medication to remove: "
        select_one_remove: str = "Select one of the strengths to remove (numbers only): "
        remove_sure: str = "Are you sure you want to remove {m} with strength {s} [0/1]?: "

        prompt_add_stock: str = "Enter the full name of the medication to add pills to: "
        select_one_add: str = "Select one of the strengths to add pills to (numbers only): "
        add_how_many: str = "How many pills to add? (numbers only): "

        exists: str = "Medication with this name already exists as:\n\n"
        exists_sure: str = "Are you sure you want to add a different strength? [0/1]: "

        prompt_subtract: str = "Type in the full name of the medication to subtract stock from: "
        select_one_subtract: str = "Select one of the strengths to subtract stock from (numbers only): "
        subtract_how_many: str = "How many pills to subtract from stock? (numbers only): "

        prompt_edit_stock: str = "Enter the full name of the medication to edit the stock of: "
        select_one_edit: str = "Select the strength of the medication to edit (numbers only): "
        set_to_what: str = "Enter the stock to set this medication to (numbers only): "

        find_name: str = "Name of the medication to find (can be partial): "

        found_these: str = "Found the following medications with name {m}:"

        NOT_IMPLEMENTED: str = "Not currently implemented. Callback correct"
        INVALID_INPUT: str = "Invalid input, please try again."
        NOT_CONNECTED: str = "Something went wrong connecting to the DB."
        ONLY_LETTERS: str = "The name of the medication must only contain letters."
        ONLY_NUMBERS: str = "Strength of the medication must only contain numbers."
        NOT_EMPTY_OR_SPECIAL: str = "The name of the medication must not be empty or contain any other character than letters."
        INVALID_CHARACTERS: str = "One of the values entered has invalid characters."
        USER_CANCEL: str = "Operation cancelled by user, failed to edit DB."
        STRENGTH_NOT_EMPTY: str = "Strength of the medication must not be empty."
        STOCK_OVERLOAD: str = "Cannot remove {p} pills from medication with stock {m}. Database modification failed."
        DUPLICATE_MED: str = "A medication with this strength already exists, duplicates are not allowed. Database modification failed."
        NO_SUCH_STRENGTH: str = "Strength of the medication did not match any existing ones, try again."
        ADD_SUCCESS: str = "Successfully added {p} pils to medication with name {m}. Med ID: {i}"
        INSERTED_SUCCESS: str = "Inserted med with ID:"
        REMOVE_SUCCESS: str = "Removed med with ID:"
        SUBTRACT_SUCCESS: str = "Subtracted {p} pills from med named {m}. Med ID: {i}"
        EDIT_SUCCESS: str = "Set medication {m}'s stock to {p}. Med ID: {i}"
        HANDSHAKE_FAILED: str = "Your IP is not allowed to make changes in the DB. Please contact the system administrator."
        NO_MEDS: str = "No medications found with the name \"{m}\""


@dataclass(frozen=True)
class Paths:
    environment_path: str = ".\\credentials\\creds.env"