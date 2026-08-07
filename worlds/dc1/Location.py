from BaseClasses import Location, Region
from worlds.dc1.game_id import dc1_name

shop_locations_to_id = {"Gaffer's Shop Item 1": 97111_1300}, {"Gaffer's Shop Item 2": 97111_1301}, \
                       {"Wise Owl Shop Item 1": 97111_2300}, {"Wise Owl Shop Item 2": 97111_2301}, \
                       {"Ruty's Shop Item 1": 97111_3300}, {"Ruty's Shop Item 2": 97111_3301}, \
                       {"Suzy's Shop Item 1": 97111_3310}, {"Suzy's Shop Item 2": 97111_3311}, \
                       {"Lana's Shop Item 1": 97111_3320}, {"Lana's Shop Item 2": 97111_3321}, \
                       {"Jack's Shop Item 1": 97111_3330}, {"Jack's Shop Item 2": 97111_3331}, \
                       {"Joker's Shop Item 1": 97111_3340}, {"Joker's Shop Item 2": 97111_3341}, \
                       {"Brooke's Shop Item 1": 97111_4300}, {"Brooke's Shop Item 2": 97111_4301}, \
                       {"Ledan's Shop Item 1": 97111_5300}, {"Ledan's Shop Item 2": 97111_5301}, \
                       {"Fairy King's Item Shop Item 1": 97111_6300}, {"Fairy King's Item Shop Item 2": 97111_6301}, \
                       {"Fairy King's Gem Shop Item 1": 97111_6310}, {"Fairy King's Gem Shop Item 2": 97111_6311}, \
                       {"Fairy King's Attachment Shop Item 1": 97111_6320}, {"Fairy King's Attachment Shop Item 2": 97111_6321}

class DarkCloudLocation(Location):
    game = dc1_name

    def __init__(self, player, name, address, loc_type, region: Region, access=None, event=None):
        super(DarkCloudLocation, self).__init__(player, name, address)
        self.type = loc_type
        self.parent_region = region
        self.access = access
