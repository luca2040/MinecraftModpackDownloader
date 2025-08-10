from print_color import print

import sys
from utils import file_input_dialog, wait_for_input, set_windows_dpi_awareness
from modpack import is_modpack_valid
from modpack_download import extract_modpack

if __name__ == "__main__":
    set_windows_dpi_awareness()  # Get correct dialog window scaling in windows

    print("Curseforge modpack downloader", color="green", format="underline")
    print()

    ############### ZIP file selection ###############

    print("Select the modpack ZIP file", color="m", format="bold")
    modpack_path = file_input_dialog(extension="zip")

    if not modpack_path:
        print("Cancelled", color="r")
        wait_for_input()
        sys.exit(0)

    print(modpack_path, tag="Selected file", color="w", tag_color="y")
    print()

    ############### Is modpack valid check ###############

    modpack_valid = is_modpack_valid(modpack_path)

    if not modpack_valid:
        print("Selected modpack is not valid", tag="Error", tag_color="r", color="r")
        wait_for_input()
        sys.exit(0)

    ############### Output path selection ###############

    print(
        "Select the path where the modpack will be downloaded", color="m", format="bold"
    )
    extraction_path = file_input_dialog(folder_dialog=True)

    if not extraction_path:
        print("Cancelled", color="r")
        wait_for_input()
        sys.exit(0)

    print(extraction_path, tag="Selected folder", color="w", tag_color="y")
    print()

    ############### Download the modpack ###############

    extract_modpack(modpack_path, extraction_path)

    wait_for_input()
