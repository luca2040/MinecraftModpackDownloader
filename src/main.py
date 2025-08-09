from print_color import print

from utils import file_input_dialog
from modpack import is_modpack_valid, extract_modpack

if __name__ == "__main__":
    print("Curseforge modpack downloader", color="green", format="underline")
    print()

    print("Select the modpack ZIP file", color="m", format="bold")
    modpack_path = file_input_dialog(extension="zip")
    if not modpack_path:
        exit()
    print(modpack_path, tag="Selected file", color="w", tag_color="y")
    print()

    modpack_valid = is_modpack_valid(modpack_path)
    if not modpack_valid:
        print("Selected modpack is not valid", tag="Error", tag_color="r", color="r")
        exit()

    print(
        "Select the path where the modpack will be downloaded", color="m", format="bold"
    )
    extraction_path = file_input_dialog(folder_dialog=True)
    if not extraction_path:
        exit()
    print(extraction_path, tag="Selected folder", color="w", tag_color="y")
    print()

    extract_modpack(modpack_path, extraction_path)
