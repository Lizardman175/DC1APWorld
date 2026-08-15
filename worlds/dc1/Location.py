from BaseClasses import Location, Region, LocationProgressType
from worlds.dc1.game_id import dc1_name, base_id

# Location ID patterns: (all prefixed with 97111)
# Atla  ABxx: A = Dungeon index 1-6, B = 1/2 for front/rear atla, xx = atla id
# MCs   A0XX: A = Town index 1-5, 0 = MC location category, xx = chest ID
# Shops A3Bx: A = Town index 1-6, 3 = shop items category, B = shop index relative to town, x = item
# Floor A4xx: A = Dungeon index 1-6, 4 = floor clear category, xx = floor value 1 indexed
# Fish  04xx: 04 = Fish location category, xx = fish item
#

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

floors = {"DBC": [1, 2, 3, 5, 6, 7, 9, 10, 12, 13, 14],
          "WOF": [1, 2, 3, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16],
          "SW":  [1, 2, 3, 4, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17],
          "SMT": [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17],
          "MS":  [1, 2, 3, 5, 6, 7, 9, 10, 12, 13, 14],
          "GOT": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24],
          "DS":  [5, 15, 25, 35, 45, 55, 65, 75]}

char_floors = {"DBC": [11],
               "WOF": [4, 12],
               "SW":  [5, 12],
               "SMT": [5, 13],
               "MS":  [4, 11],
               "GOT": [19, 20, 21, 22, 23]}

def floor_location_ids() -> dict[str, int]:
    ids = {}
    count = 0
    for dun in floors.keys():
        count += 1
        for floor in floors[dun]:
            ids["Clear " + dun + " Floor " + str(floor)] = base_id + (count * 1000) + 400 + floor

    count = 0
    for dun in char_floors.keys():
        count += 1
        for char_floor in char_floors[dun]:
            ids["Clear " + dun + " Floor " + str(char_floor)] = base_id + (count * 1000) + 400 + char_floor

    return ids

class DarkCloudLocation(Location):
    game = dc1_name

    def __init__(self, player, name, address, loc_type, region: Region, access=None, event=None):
        super(DarkCloudLocation, self).__init__(player, name, address)
        self.type = loc_type
        self.parent_region = region
        self.access = access

def floor_locations(player: int, boss_goal: int, floor_sanity: int, idea: int, regions: list[Region]) -> int:
    loc_count = 0
    if floor_sanity == 0:
        return loc_count

    count = 0
    for dun in floors.keys():
        for floor in floors[dun]:
            region = regions[count + 1] if count < 10 and floor > 8 else regions[count]
            region.locations.append(DarkCloudLocation(player, "Clear " + dun + " Floor " + str(floor),
                                                      int(base_id + ((count / 2 + 1) * 1000) + 400 + floor),
                                                      LocationProgressType.DEFAULT, region))
            loc_count += 1
        count += 2
        if count / 2 == boss_goal:
            break

    if idea > 0:
        region = regions[10]
        for floor in floors["DS"]:
            region.locations.append(DarkCloudLocation(player, "Clear DS Floor " + str(floor),
                                                      int(base_id + (7 * 1000) + 400 + floor),
                                                      LocationProgressType.PRIORITY, region))
            loc_count += 1

    if floor_sanity > 1:
        count = 0
        for dun in char_floors.keys():
            for floor in char_floors[dun]:
                region = regions[count + 1] if count < 10 and floor > 8 else regions[count]
                region.locations.append(DarkCloudLocation(player, "Clear " + dun + " Floor " + str(floor),
                                                          int(base_id + ((count / 2 + 1) * 1000) + 400 + floor),
                                                          LocationProgressType.DEFAULT, region))
                loc_count += 1
            count += 2
            if count / 2 == boss_goal:
                break

    return loc_count
