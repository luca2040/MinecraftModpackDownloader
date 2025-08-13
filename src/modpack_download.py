from typing import List
from print_color import print
import os
import sys
import time
import concurrent.futures

from modpack import Modpack
from utils import extract_zip_subfolder, print_progress
from mod import mod_type_names_map, mod_type_color_map
from download_list import ask_download_list


NUM_RETRIES = 5  # Maximum number of download retires
RETRY_DELAY = 2  # Delay between retries in seconds

README_NAME = "MODPACK_DOWNLOAD_README.txt"


def mod_download(modpack: Modpack, mod_index: int) -> int | None:
    """Tries to download a mod from the modpack.

    Args:
        modpack (Modpack): The Modpack instance
        mod_index (int): The mod index

    Returns:
        int | None: None if the mod was successfully downloaded, otherwise the mod's index
    """
    exists = modpack.request_filename(mod_index)
    if not exists:
        return mod_index

    for _ in range(NUM_RETRIES):
        success = modpack.download_resource(mod_index)
        if success:
            return None

        time.sleep(RETRY_DELAY)

    return mod_index


def multithreaded_download(modpack: Modpack) -> List[int]:
    """Downloads concurrently all the mods in the modpack.

    Args:
        modpack (Modpack): The Modpack instance

    Returns:
        List[int]: A list containing the indices of each mod that failed the download
    """
    error_list: List[int] = []

    max_workers = (os.cpu_count() or 1) * 5
    progress_idx = 0
    modpack_len = len(modpack)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        submits = [
            executor.submit(mod_download, modpack, idx) for idx, _ in enumerate(modpack)
        ]

        for completed in concurrent.futures.as_completed(submits):
            eventual_error: int | None = completed.result()
            if eventual_error is not None:
                error_list.append(eventual_error)

            progress_idx = progress_idx + 1
            print_progress(progress_idx, modpack_len)

    return error_list


def extract_modpack(modpack_path: str, extraction_path: str) -> Modpack | None:
    """Extracts the modpack to the given folder.

    Args:
        modpack_path (str): The path to the modpack's ZIP file
        extraction_path (str): The path to the folder where the modpack will be extracted to
    """
    modpack = Modpack(modpack_path, extraction_path)

    if not modpack.load_modpack():
        print("Error loading the modpack", tag="Error", tag_color="r", color="r")
        return

    print("Downloading mods", color="c", format="bold")
    error_indices = multithreaded_download(modpack)

    print()
    print("Download finished", color="g", format="bold")
    if error_indices:
        total = len(modpack)
        failed = len(error_indices)
        err_percent = failed / total * 100

        print(
            f"Errors downloading {failed} resources out of {total} "
            f"({err_percent:.1f}%):",
            color="r",
        )

        for error_idx in error_indices:
            mod_element = modpack[error_idx]
            name_str: str = (
                mod_element.view_name
                or f"{mod_element.project_id}:{mod_element.file_id}"
            )

            tag_str = mod_type_names_map[mod_element.file_type]
            tag_col = mod_type_color_map[mod_element.file_type]

            sys.stdout.write("    ")
            sys.stdout.flush()
            print(" " + name_str, tag=tag_str, tag_color=tag_col, color="w")

        ask_download_list(modpack, error_indices)

    if modpack.overrides is not None:
        print()
        print("Extracting overrides", color="c", format="bold")
        extract_zip_subfolder(
            zip_path=modpack_path, subfolder=modpack.overrides, dest_dir=extraction_path
        )
        print("Overrides extracted", color="g", format="bold")

    modpack_description = f"{modpack.modpack_name} - {modpack.modpack_version}"
    if modpack.modpack_author:
        modpack_description += f" by {modpack.modpack_author}"

    readme_path = os.path.join(extraction_path, README_NAME)
    readme_contents = (
        f"{modpack_description}\n\n"
        f"Minecraft {modpack.minecraft_version}\n"
        f"Total resources (mods, resourcepacks and shaders): {len(modpack.mods)}"
    )

    with open(readme_path, "w") as readme_file:
        readme_file.write(readme_contents)

    print()
    print("Modpack successfully downloaded", color="g", format="bold")

    return modpack
