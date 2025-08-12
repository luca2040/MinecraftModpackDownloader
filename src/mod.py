from enum import Enum, EnumMeta
from typing import Dict, cast
from print_color.print_color import Color as color_typing


class ModTypeMeta(EnumMeta):
    """Metaclass for the ModType enum to get the corresponding type from the curseforge tag in the url"""

    def __getitem__(cls, name: str):
        cls = cast("ModType", cls)
        match name.lower():
            case "mc-mods":
                return cls.MOD
            case "texture-packs":
                return cls.RESOURCEPACK
            case "shaders":
                return cls.SHADERPACK
            case _:
                return cls.DEFAULT


class ModType(Enum, metaclass=ModTypeMeta):
    """Enum of the file types in modpacks."""

    DEFAULT = 0  # If it cant be loaded from the modlist file
    MOD = 1
    RESOURCEPACK = 2
    SHADERPACK = 3


class ModElement:
    """Class to represent each mod file in the modpack"""

    def __init__(self, project_id: int, file_id: int):
        self.project_id: int = project_id
        self.file_id: int = file_id
        self.filename: str = ""

        self.file_type: ModType = ModType.DEFAULT

        # Loaded from the  modlist.html file
        self.view_name: str | None = None
        self.curseforge_url: str | None = None


mod_type_names_map: Dict[ModType, str] = {
    ModType.MOD: "     MOD     ",
    ModType.RESOURCEPACK: "RESOURCE PACK",
    ModType.SHADERPACK: "   SHADER    ",
    ModType.DEFAULT: "  UNDEFINED  ",
}

mod_type_color_map: Dict[ModType, color_typing] = {
    ModType.MOD: "c",
    ModType.RESOURCEPACK: "y",
    ModType.SHADERPACK: "m",
    ModType.DEFAULT: "w",
}
