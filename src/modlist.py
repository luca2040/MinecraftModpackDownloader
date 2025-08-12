from typing import List, Iterator, TypedDict
import bs4
from bs4 import BeautifulSoup

from utils import load_file_from_zip
from mod import ModType


class ModDict(TypedDict):
    name: str
    url: str
    type: ModType


class Modlist:
    def _get_type(self, url: str) -> ModType:
        element_url_parts = url.split("/")
        if len(element_url_parts) < 2:
            return ModType.DEFAULT

        type_str = element_url_parts[-2]
        return ModType[type_str]

    def __init__(self, modpack_path: str, modlist_file: str) -> None:
        self.modpack_path: str = modpack_path
        self.modlist_file: str = modlist_file

        try:
            html_bytes = load_file_from_zip(self.modpack_path, self.modlist_file)
            loaded_html = BeautifulSoup(html_bytes, "html.parser")

            self.loaded_mods: List[ModDict] = []
            for link in loaded_html.find_all("a"):
                if isinstance(link, bs4.Tag) and link.has_attr("href"):
                    name = link.text.strip()
                    url = str(link.get("href", ""))

                    self.loaded_mods.append(
                        {"name": name, "url": url, "type": self._get_type(url)}
                    )

            self.is_valid = True
        except:
            self.is_valid = False

    def __getitem__(self, idx: int) -> ModDict | None:
        if not self.is_valid:
            return None
        return self.loaded_mods[idx]

    def __len__(self) -> int:
        if not self.is_valid:
            return 0
        return len(self.loaded_mods)

    def __iter__(self) -> Iterator[ModDict]:
        if not self.is_valid:
            return iter([])
        return iter(self.loaded_mods)
