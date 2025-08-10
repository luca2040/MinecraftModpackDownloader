from typing import Dict
from print_color import print
import zipfile
import json
import os
import sys
import time
import concurrent.futures
import threading

from cursemaven import mod_name_from_id, download_mod
from utils import extract_zip_subfolder

MANIFEST_FILE = "manifest.json"

NUM_RETRIES = 5
RETRY_DELAY = 2


def is_modpack_valid(modpack_path: str) -> bool:
    """Checks if a modpack is valid

    Args:
        modpack_path (str): The modpack's ZIP file path

    Returns:
        bool: True if the pack is valid, false otherwise
    """
    try:
        with zipfile.ZipFile(modpack_path, "r") as z:
            return MANIFEST_FILE in z.namelist()
    except:
        return False


def get_minecraft_version(modpack_content: Dict) -> str:
    """Gets the minecraft version for the given manifest dict

    Args:
        modpack_content (Dict): The manifest json file loaded as a Python dict

    Returns:
        str: The minecraft version as "version - loader id"
    """
    minecraft = modpack_content.get("minecraft", None)
    if not minecraft:
        return ""

    version = minecraft.get("version", "")
    modloaders = minecraft.get("modLoaders", [])

    id = ""

    for loader in modloaders:
        is_primary = loader.get("primary", False)
        current_id = loader.get("id", "")
        if is_primary:
            id = current_id

    return f"{version} - {id}"


def check_and_download_resource(
    project_id, file_id, mod_name, resourcepack_folder, mods_folder
) -> bool:  # True means that there is no need to retry
    is_texturepack = mod_name.endswith(".zip")  # Not the best check, but it works
    target_folder = resourcepack_folder if is_texturepack else mods_folder
    download_filepath = os.path.join(target_folder, mod_name)

    downloaded = download_mod(mod_name, download_filepath, project_id, file_id)
    return downloaded


def download_wrapper(args) -> str | None:
    idx, file, resourcepack_folder, mods_folder = args

    project_id = file.get("projectID", None)
    file_id = file.get("fileID", None)

    if project_id is None or file_id is None:
        return

    mod_name = mod_name_from_id(project_id, file_id)
    if not mod_name:
        return f"{project_id}:{file_id}"

    for _ in range(NUM_RETRIES):
        success = check_and_download_resource(
            project_id=project_id,
            file_id=file_id,
            mod_name=mod_name,
            resourcepack_folder=resourcepack_folder,
            mods_folder=mods_folder,
        )
        if success:
            return
        time.sleep(RETRY_DELAY)

    return mod_name


def multithreaded_download(files, resourcepack_folder, mods_folder):
    files_args = [
        (idx, file, resourcepack_folder, mods_folder) for idx, file in enumerate(files)
    ]
    total_files = len(files)
    print_lock = threading.Lock()

    def print_progress(print_idx) -> None:
        p = print_idx / total_files
        i = int(p * 40)
        sys.stdout.write("\r")
        sys.stdout.write("[%-40s] %.2f%%" % ("=" * i, p * 100))
        sys.stdout.flush()

    error_list = []

    max_workers = (os.cpu_count() or 10) * 5
    idx = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(download_wrapper, arg) for arg in files_args]
        for future in concurrent.futures.as_completed(futures):
            with print_lock:
                eventual_error = future.result()
                if eventual_error:
                    error_list.append(eventual_error)
                idx = idx + 1
                print_progress(idx)

    return error_list


def extract_modpack(modpack_path: str, extraction_path: str) -> None:
    try:
        with zipfile.ZipFile(modpack_path, "r") as z:
            with z.open(MANIFEST_FILE) as f:
                json_bytes = f.read()
                json_str = json_bytes.decode("utf-8")
                manifest = json.loads(json_str)
    except:
        print("Error parsing manifest file", tag="Error", tag_color="r", color="r")
        return

    overrides = manifest.get("overrides", None)
    minecraft_version = get_minecraft_version(manifest)
    modpack_name = manifest.get("name", "")
    modpack_version = manifest.get("version", "")
    modpack_author = manifest.get("author", "")
    files = manifest.get("files", None)

    mods_folder = os.path.join(extraction_path, "mods")
    resourcepack_folder = os.path.join(extraction_path, "resourcepacks")
    os.makedirs(mods_folder, exist_ok=True)
    os.makedirs(resourcepack_folder, exist_ok=True)

    print("Downloading mods", color="c", format="bold")
    errors = multithreaded_download(
        files, resourcepack_folder=resourcepack_folder, mods_folder=mods_folder
    )

    print()
    print("Download finished", color="g", format="bold")
    if errors:
        print("Errors downloading:", color="r")
        for error in errors:
            print("\t" + error)

    if overrides is not None:
        print()
        print("Extracting overrides", color="c", format="bold")
        extract_zip_subfolder(
            zip_path=modpack_path, subfolder=overrides, dest_dir=extraction_path
        )
        print("Overrides extracted", color="g", format="bold")

    modpack_description = f"{modpack_name} - {modpack_version}"
    if modpack_author:
        modpack_description += f" by {modpack_author}"

    readme_path = os.path.join(extraction_path, "README_MODPACK.txt")
    readme_contents = (
        f"{modpack_description}\n\n"
        f"Minecraft {minecraft_version}\n"
        f"Total resources (mods, resourcepacks and shaders) downloaded: {len(files)}"
    )

    with open(readme_path, "w") as readme_file:
        readme_file.write(readme_contents)

    print()
    print("Modpack successfully downloaded", color="g", format="bold")
