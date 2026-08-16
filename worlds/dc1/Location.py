from BaseClasses import Location, Region, LocationProgressType
from worlds.dc1.game_id import dc1_name, base_id

# Location ID patterns: (all prefixed with 97111)
# MCs   0BXX: 0 = MC location category, B = Town index 1-5, xx = chest ID
# Atla  ABxx: A = 1/2 for front/rear atla, B = Dungeon index 1-6, xx = atla id
# Shops 3ABx: 3 = shop location category, A = Town index 1-6, B = shop index relative to town, x = item 1/2
# Fish  40xx: 40 = Fish location category, xx = fish item
# Floor 4Axx: 4[1-6] = floor clear category, A = Dungeon index 1-6, xx = floor value 1 indexed
#

shop_locations_to_id = {"Gaffer's Shop Item 1": 97111_3100}, {"Gaffer's Shop Item 2": 97111_3101}, \
                       {"Wise Owl Shop Item 1": 97111_3200}, {"Wise Owl Shop Item 2": 97111_3201}, \
                       {"Ruty's Shop Item 1": 97111_3300}, {"Ruty's Shop Item 2": 97111_3301}, \
                       {"Suzy's Shop Item 1": 97111_3310}, {"Suzy's Shop Item 2": 97111_3311}, \
                       {"Lana's Shop Item 1": 97111_3320}, {"Lana's Shop Item 2": 97111_3321}, \
                       {"Jack's Shop Item 1": 97111_3330}, {"Jack's Shop Item 2": 97111_3331}, \
                       {"Joker's Shop Item 1": 97111_3340}, {"Joker's Shop Item 2": 97111_3341}, \
                       {"Brooke's Shop Item 1": 97111_3400}, {"Brooke's Shop Item 2": 97111_3401}, \
                       {"Ledan's Shop Item 1": 97111_3500}, {"Ledan's Shop Item 2": 97111_3501}, \
                       {"Fairy King's Item Shop Item 1": 97111_3600}, {"Fairy King's Item Shop Item 2": 97111_3601}, \
                       {"Fairy King's Gem Shop Item 1": 97111_3610}, {"Fairy King's Gem Shop Item 2": 97111_3611}, \
                       {"Fairy King's Attachment Shop Item 1": 97111_3620}, \
                       {"Fairy King's Attachment Shop Item 2": 97111_3621}

fish_locations_to_id = ({"Catch a Bobo": 97111_4000}, {"Catch a Gobbler": 97111_4001},
                        {"Catch a Nonky": 97111_4002}, {"Catch a Kaji": 97111_4003},
                        {"Catch a Baku Baku": 97111_4004}, {"Catch a Mardan Garayan": 97111_4005},
                        {"Catch a Gummy": 97111_4006}, {"Catch a Niler": 97111_4007},  # No 8, duplicate ID in game
                        {"Catch an Umadakara": 97111_4009}, {"Catch a Tarton": 97111_4010},
                        {"Catch a Piccoly": 97111_4011}, {"Catch a Bon": 97111_4012},
                        {"Catch a Hama Hama": 97111_4013}, {"Catch a Negie": 97111_4014},
                        {"Catch a Den": 97111_4015}, {"Catch a Heela": 97111_4016},
                        {"Catch a Baron Garayan": 97111_4017})

floors = {"DBC": [1, 2, 3, 5, 6, 7, 9, 10, 12, 13, 14],
          "WOF": [1, 2, 3, 5, 6, 7, 8, 10, 11, 13, 14, 15, 16],
          "SW":  [1, 2, 3, 4, 6, 7, 8, 10, 11, 13, 14, 15, 16, 17],
          "SMT": [1, 2, 3, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17],
          "MS":  [1, 2, 3, 5, 6, 7, 9, 10, 12, 13, 14],
          "GOT": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 24]}

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
            ids["Clear " + dun + " Floor " + str(floor)] = base_id + (count * 100) + 4000 + floor

    count = 0
    for dun in char_floors.keys():
        count += 1
        for char_floor in char_floors[dun]:
            ids["Clear " + dun + " Floor " + str(char_floor)] = base_id + (count * 100) + 4000 + char_floor

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
                                                      int(base_id + ((count / 2 + 1) * 100) + 4000 + floor),
                                                      LocationProgressType.DEFAULT, region))
            loc_count += 1
        count += 2
        if count / 2 == boss_goal:
            break

    if idea > 0:
        region = regions[10]
        for floor in [5, 15, 25, 35, 45]:
            region.locations.append(DarkCloudLocation(player, "Clear DS Floor " + str(floor),
                                                      int(base_id + (7 * 100) + 4000 + floor),
                                                      LocationProgressType.PRIORITY, region))
            loc_count += 1

    if floor_sanity > 1:
        count = 0
        for dun in char_floors.keys():
            for floor in char_floors[dun]:
                region = regions[count + 1] if count < 10 and floor > 8 else regions[count]
                region.locations.append(DarkCloudLocation(player, "Clear " + dun + " Floor " + str(floor),
                                                          int(base_id + ((count / 2 + 1) * 100) + 4000 + floor),
                                                          LocationProgressType.DEFAULT, region))
                loc_count += 1
            count += 2
            if count / 2 == boss_goal:
                break

    return loc_count
