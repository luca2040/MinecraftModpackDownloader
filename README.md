# Minecraft Modpack Downloader
Simple program to download Minecraft CurseForge modpacks into a folder containing all the modpack's mods, resourcepacks and custom configurations.

>[!NOTE]
>This program takes the most important information from the modpack's `manifest.json` and it actually ignores the `manifestType` and `manifestVersion` fields, so there may be rare cases of issues related to this.
><br/>However i still haven't seen any issues even after trying some of the most used modpacks, so i think this is fine.

## Description
Modpacks do not contain the actual mod files into their zip file, but instead they contain a file that indicates all the mods' IDs to download them.
<br/>This program takes all the mod's IDs and downloads them from the [cursemaven](https://cursemaven.com) repository, then it takes all the custom overrides from the pack's zip and extracts them directly in the extraction folder.
<br/>At the end, the program creates a `README_MODPACK.txt` that contains the pack's information and the required minecraft + loader version to run it.

## Usage
- Run the program.
- You will be prompted to select the modpack ZIP file.
- Next, choose the extraction path - this is the folder where the modpack files will be downloaded and extracted. It can be any directory on your system.

The program will then:
- Download all the mods and resource packs.
- Extract the modpack files into the chosen folder.
- Create a `README_MODPACK.txt` file inside the extraction folder with information about the modpack.

Example `README_MODPACK.txt`:
```txt
Example modpack - 1.0.0 by Example author

Minecraft 1.18.2 - forge-40.2.34
Total resources (mods and resourcepacks): 24
```

After extraction, you can:
- Set up your Minecraft instance the way you prefer with the loader version specified in the readme - no specific launcher needed.
- Manually copy the modpack files from the extraction folder to your Minecraft instance folder as desired.
