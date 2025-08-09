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
