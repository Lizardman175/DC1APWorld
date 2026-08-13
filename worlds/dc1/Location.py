from BaseClasses import Location, Region
from worlds.dc1.game_id import dc1_name

# Location ID patterns: (all prefixed with 97111)
# Atla  ABxx: A = Town index 1-6, B = 1/2 for front/rear atla, xx = atla id
# MCs   A0XX: A = Town index 1-5, 0 = MC location category, xx = chest ID
# Shops A3Bx: A = Town index, 3 = shop items category, B = shop index relative to town, x = item
# Fish  04xx: 04 = Fish location category, xx = fish item
#
# Special Location IDs:
# Dark Genie flag  9999

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
                       {"Fairy King's Attachment Shop Item 1": 97111_6320}, \
                       {"Fairy King's Attachment Shop Item 2": 97111_6321}

fish_locations_to_id = ({"Catch a Bobo": 97111_0400}, {"Catch a Gobbler": 97111_0401},
                        {"Catch a Nonky": 97111_0402}, {"Catch a Kaji": 97111_0403},
                        {"Catch a Baku Baku": 97111_0404}, {"Catch a Mardan Garayan": 97111_0405},
                        {"Catch a Gummy": 97111_0406}, {"Catch a Niler": 97111_0407},  # No 8, duplicate ID in game
                        {"Catch an Umadakara": 97111_0409}, {"Catch a Tarton": 97111_0410},
                        {"Catch a Piccoly": 97111_0411}, {"Catch a Bon": 97111_0412},
                        {"Catch a Hama Hama": 97111_0413}, {"Catch a Negie": 97111_0414},
                        {"Catch a Den": 97111_0415}, {"Catch a Heela": 97111_0416},
                        {"Catch a Baron Garayan": 97111_0417})

class DarkCloudLocation(Location):
    game = dc1_name

    def __init__(self, player, name, address, loc_type, region: Region, access=None, event=None):
        super(DarkCloudLocation, self).__init__(player, name, address)
        self.type = loc_type
        self.parent_region = region
        self.access = access
