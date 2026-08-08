import re

from BaseClasses import Item, ItemClassification
from .game_id import dc1_name

# Item ID patterns: (all prefixed with 97111)
# Georama     0Axx:  0 = Georama, A = town index, xx = georama piece
# Consumables 1xxx:  1 = Consumable item category, xxx = item ID from game
# Attachments 2xxx:  2 = Attachment item category, xxx = item ID from game
# +x attach   20AB: 20 = Attachment, A = type 0-3 (att/speed/end/mag), B = +1/2/3
# Weapons     3xxx:  3 = Weapon item category, xxx = item ID from game (unused)
#
# Special Item IDs:
# Progressive Char Building 0000
# Dark Genie flag           9999

class DarkCloudItem(Item):
    game = dc1_name

class ItemData:
    classification = ItemClassification.trap # Should never see a Trap currently
    name = None
    ap_id = 0
    count = 0

    def __init__(self, name: str, ap_id: int, classification: ItemClassification, counts):
        self.name = name
        self.ap_id = ap_id
        self.counts = counts
        self.classification = classification

    def to_items(self, player: int, world) -> list[DarkCloudItem]:
        items = []

        for j in range(0, min(5, world.options.boss_goal)):
            # Randomize the +x value for attack, speed, endurance, magic attachments on the server
            if 971112000 < self.ap_id <= 971112033:
                for i in range(self.counts[j]):
                    items.append(self.to_stat_item(player, world))
            else:
                for i in range(self.counts[j]):
                    items.append(DarkCloudItem(self.name, self.classification, self.ap_id, player))

        return items

    def to_item(self, player: int, world) -> DarkCloudItem:
        # Randomize the +x value for attack, speed, endurance, magic attachments on the server
        if 971112000 < self.ap_id <= 971112033:
            item = self.to_stat_item(player, world)
        else:
            item = DarkCloudItem(self.name, self.classification, self.ap_id, player)

        return item

    def to_stat_item(self, player: int, world) -> DarkCloudItem:
        temp_ap_id = self.ap_id
        rand = world.random.randint(0, 2)
        temp_ap_id = temp_ap_id + rand
        temp_name = re.search('(.*\\+)', self.name).group(0) + str(rand + 1)
        return DarkCloudItem(temp_name, self.classification, temp_ap_id, player)
