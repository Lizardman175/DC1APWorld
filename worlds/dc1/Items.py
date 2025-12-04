import json
import pkgutil

from BaseClasses import Item, ItemClassification
from worlds.dc1.game_id import dc1_name

prog_map = json.loads(pkgutil.get_data(__name__, "data/progressive.json").decode())

progressive_item_list = {}
for prog_item in prog_map:
    progressiveName = prog_map[prog_item]
    if progressiveName not in progressive_item_list:
        progressive_item_list[progressiveName] = []
    progressive_item_list[progressiveName].append(prog_item)

class DarkCloudItem(Item):
    game: str = dc1_name

    def __init__(self, name: str,
                 classification: ItemClassification,
                 code: int | None,
                 player: int):
        super().__init__(name, classification, code, player)
        self.game = dc1_name

class ItemData:
    classification = ItemClassification.trap
    name = None
    ap_id = 0
    count = 0

    def __init__(self, name: str, ap_id: int, classification: int, count: int):
        self.name = name
        self.ap_id = ap_id
        self.count = count
        if classification == 0:
            self.classification = ItemClassification.filler
        elif classification == 1:
            self.classification = ItemClassification.useful
        elif classification == 2:
            self.classification = ItemClassification.progression

    def to_items(self, player: int) -> list[DarkCloudItem]:
        items = []

        for i in range(self.count):
            items.append(DarkCloudItem(self.name, self.classification, self.ap_id, player))

        return items