from pathlib import Path
import os
import sys
import ctypes
import zipfile
import tkinter as tk
from tkinter import filedialog


def set_windows_dpi_awareness():
    """Sets the DPI scaling on windows.
    Safely detects if the current platform is not windows."""
    if sys.platform == "win32":
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass


def file_input_dialog(extension: str | None = None, folder_dialog: bool = False) -> str:
    """Opens a file/folder input dialog using tkinter.

    Args:
        extension (str | None, optional): If folder_dialog is false, this is the
            file extension that files will be filtered for in the file input dialog. Defaults to None.
        folder_dialog (bool, optional): True if this is a folder input dialog, False for a file input dialog.
            For file input dialogs, extension is needed. Defaults to False.

    Returns:
        str: The resulting path.
    """
    if extension is None and not folder_dialog:
        return ""

    root = tk.Tk()
    root.withdraw()

    root.overrideredirect(True)
    root.geometry("0x0+0+0")

    root.deiconify()
    root.lift()
    root.focus_force()

    if folder_dialog:
        filename = filedialog.askdirectory(parent=root)
    else:
        assert extension is not None
        ext = extension if extension.startswith("*") else f"*{extension}"
        filename = filedialog.askopenfilename(parent=root, filetypes=[("File", ext)])

    root.destroy()

    return filename


def load_file_from_zip(zip_path: str, file_in_zip: str) -> bytes:
    """Loads a file from a ZIP file

    Args:
        zip_path (str): Path to the ZIP file
        file_in_zip (str): Path to the file in the ZIP, relative to it.

    Returns:
        bytes: The loaded file
    """
    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open(file_in_zip) as f:
            return f.read()


def extract_zip_subfolder(zip_path: str, subfolder: str, dest_dir: str) -> None:
    """Extracts a folder thats inside a ZIP file to a folder on disk.
    Used to extract the overrides folder from the modpack's ZIP to the output path.

    Args:
        zip_path (str): The input ZIP file path
        subfolder (str): The folder inside the ZIP relative to it
        dest_dir (str): The destination path
    """
    subfolder = subfolder.strip("/")
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.namelist():
            if member.endswith("/"):
                continue  # Skip dirs

            # If the current file is in the selected subfolder
            if subfolder == "." or member.startswith(subfolder + "/"):
                relative_path = (
                    member if subfolder == "." else member[len(subfolder) + 1 :]
                )
                target_path = Path(dest_dir) / relative_path

                os.makedirs(target_path.parent, exist_ok=True)

                with z.open(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())


def print_progress(current_idx: int, total_len: int) -> None:
    """Prints a progress bar on the current line, overwriting what was there before.
    Can be called consecutively to make the bar progress without needing a new line.

    Args:
        current_idx (int): The current iteration index
        total_len (int): The number of iterations
    """
    p = current_idx / total_len
    i = int(p * 40)
    sys.stdout.write("\r")
    sys.stdout.write("[%-40s] %.2f%%" % ("=" * i, p * 100))
    sys.stdout.flush()


def wait_for_input() -> None:
    """Simple function that asks the user to press enter to close the program, and waits for it."""
    print()
    input("Press enter to close the program")
