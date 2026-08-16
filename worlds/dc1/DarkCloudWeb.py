from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld


# TODO webworld implementation as we get closer to completion.
class DarkCloudWeb(WebWorld):
    theme = "jungle"

    setup_en = Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Dark Cloud 1 for Archipelago.",
        "English",
        "setup_en.md",
        "setup/en",
        ["Lizardman175"]
    )

    tutorials = [setup_en]
    game_info_languages = ["en"]