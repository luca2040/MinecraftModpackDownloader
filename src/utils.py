from pathlib import Path
import os
import zipfile
import tkinter as tk
from tkinter import filedialog


def file_input_dialog(extension: str | None = None, folder_dialog: bool = False) -> str:
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
        filename = filedialog.askopenfilename(
            parent=root, filetypes=[("File", extension)]
        )

    root.destroy()

    return filename


def extract_zip_subfolder(zip_path: str, subfolder: str, dest_dir: str) -> None:
    subfolder = subfolder.strip("/")
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.namelist():
            if member.endswith("/"):
                continue  # Skip dirs

            if subfolder == "." or member.startswith(subfolder + "/"):
                relative_path = (
                    member if subfolder == "." else member[len(subfolder) + 1 :]
                )
                target_path = Path(dest_dir) / relative_path

                os.makedirs(target_path.parent, exist_ok=True)

                with z.open(member) as source, open(target_path, "wb") as target:
                    target.write(source.read())
