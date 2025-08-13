from typing import Dict, Iterator, List
import zipfile
import os
import json

from utils import load_file_from_zip
from cursemaven import mod_name_from_id, download_mod
from modlist import Modlist
from mod import ModElement, ModType

MANIFEST_FILE = "manifest.json"
MODLIST_FILE = "modlist.html"


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


def get_minecraft_version_wrapper(modpack_path: str) -> str | None:
    """Wrapper for the get_minecraft_version function that accepts the modpack path instead of the loaded content.
    Used to get the version before loading the pack.

    Args:
        modpack_path (str): The path to the pack's ZIP file

    Returns:
        str | None: The minecraft version as "version - loader id" or None if the modpack couldnt be loaded.
    """
    try:
        json_bytes = load_file_from_zip(modpack_path, MANIFEST_FILE)
        json_str = json_bytes.decode("utf-8")
        manifest = json.loads(json_str)
    except:
        return None

    version = get_minecraft_version(manifest)
    return version if version else None  # Turn the "" into None


class Modpack:
    """Class to store modpack-relative information, used to simplify passing those variables into functions."""

    def __init__(self, modpack_path: str, extraction_path: str):
        """Set the paths for the modpack.

        Args:
            modpack_path (str): Path to the modpack's ZIP file
            extraction_path (str): Output path
        """
        self.modpack_path = modpack_path
        self.output_path = extraction_path

        # Those will be set later
        self.overrides: str | None = None
        self.minecraft_version: str = ""
        self.modpack_name: str = ""
        self.modpack_version: str = ""
        self.modpack_author: str = ""
        self.mods: List[ModElement] = []

        self.mods_folder: str = os.path.join(self.output_path, "mods")
        self.resourcepack_folder: str = os.path.join(self.output_path, "resourcepacks")
        self.shaderpack_folder: str = os.path.join(self.output_path, "shaderpacks")

        self.download_html_path: str = os.path.join(
            self.output_path, "missing_mods.html"
        )

        self.folder_map: Dict[ModType, str] = {
            ModType.MOD: self.mods_folder,
            ModType.RESOURCEPACK: self.resourcepack_folder,
            ModType.SHADERPACK: self.shaderpack_folder,
        }

    def load_modpack(self) -> bool:
        """Try loading the modpack.

        Returns:
            bool: True if the pack has been loaded successfully, False otherwise.
        """
        try:
            json_bytes = load_file_from_zip(self.modpack_path, MANIFEST_FILE)
            json_str = json_bytes.decode("utf-8")
            manifest = json.loads(json_str)
        except:
            return False

        modlist = Modlist(self.modpack_path, MODLIST_FILE)

        self.overrides: str | None = manifest.get("overrides", None)
        self.minecraft_version: str = get_minecraft_version(manifest)
        self.modpack_name: str = manifest.get("name", "")
        self.modpack_version: str = manifest.get("version", "")
        self.modpack_author: str = manifest.get("author", "")

        files: List[Dict] = manifest.get("files", [])
        use_modlist: bool = len(modlist) == len(files)
        for idx, file in enumerate(files):
            proj_id = file.get("projectID")
            file_id = file.get("fileID")

            if proj_id is not None and file_id is not None:
                mod_element = ModElement(proj_id, file_id)

                if use_modlist:
                    modlist_element = modlist[idx]
                    assert modlist_element is not None

                    mod_element.view_name = modlist_element["name"]
                    mod_element.curseforge_url = modlist_element["url"]
                    mod_element.file_type = modlist_element["type"]

                self.mods.append(mod_element)

        os.makedirs(self.mods_folder, exist_ok=True)
        os.makedirs(self.resourcepack_folder, exist_ok=True)
        os.makedirs(self.shaderpack_folder, exist_ok=True)

        return True

    def __getitem__(self, idx: int):
        return self.mods[idx]

    def __len__(self) -> int:
        return len(self.mods)

    def __iter__(self) -> Iterator[ModElement]:
        return iter(self.mods)

    def request_filename(self, mod_index: int) -> bool:
        """Requests from the repo the mod's filename, to also check if it exists in there,

        Args:
            mod_index (int): The mod index

        Returns:
            bool: True if the mod exists in the repo, False otherwise
        """
        mod_element: ModElement = self[mod_index]

        filename: str | None = mod_name_from_id(
            mod_element.project_id, mod_element.file_id
        )
        if not filename:
            return False

        mod_element.filename = filename
        return True

    def download_resource(self, mod_index: int) -> bool:
        """Downloads the resource (mod or whatever) indicated by the index to its folder.

        Args:
            mod_index (int): The mod index

        Returns:
            bool: True if the mod was successfully downloaded, False otherwise.
        """

        mod_element: ModElement = self[mod_index]

        target_folder = self.folder_map.get(mod_element.file_type)
        if target_folder is None:  # If its the default file type try to guess it
            is_texturepack = mod_element.filename.endswith(".zip")
            target_folder = (
                self.resourcepack_folder if is_texturepack else self.mods_folder
            )

        download_filepath = os.path.join(target_folder, mod_element.filename)

        return download_mod(
            mod_element.filename,
            download_filepath,
            mod_element.project_id,
            mod_element.file_id,
        )

    def generate_download_url(self, mod_index: int) -> None:
        """Generates the direct download url for the mod indicated by the index.

        Args:
            mod_index (int): The mod index
        """
        mod_element: ModElement = self[mod_index]
        if mod_element.curseforge_url is None:
            return

        mod_element.download_url = (
            f"{mod_element.curseforge_url}/download/{mod_element.file_id}"
        )

    def cleanup(self) -> None:
        """Cleans up the eventual missing_mods.html file."""
        if os.path.exists(self.download_html_path):
            os.remove(self.download_html_path)
