import json
import logging
import math
import pkgutil
import typing
from typing import Mapping, Any, Optional

from BaseClasses import Region, LocationProgressType, Item, CollectionState, ItemClassification, Tutorial
from rule_builder.options import OptionFilter
from rule_builder.rules import HasAll, True_, False_, Rule
from worlds.AutoWorld import World
from .DarkCloudWeb import DarkCloudWeb
from .JunkDrawer import progressive_char_recruit_name, progressive_char_recruit_id

from .data import (NoruneGeoItems, MatatakiGeoItems, QueensGeoItems,
                   MuskaGeoItems, FactoryGeoItems, DHCGeoItems)
from .Items import DarkCloudItem, ItemData
from .Location import DarkCloudLocation, shop_locations_to_id, fish_locations_to_id, floors, char_floors
from .Options import DarkCloudOptions, MiracleSanity
from .data.MiracleChest import MiracleChest
from .data.Progressive import all_chars, split_chars
from .game_id import dc1_name, base_id
from .rules import Rules, FishRules

geo_funcs = [NoruneGeoItems.create_norune_atla, MatatakiGeoItems.create_matataki_atla,
             QueensGeoItems.create_queens_atla, MuskaGeoItems.create_muska_atla,
             FactoryGeoItems.create_factory_atla, DHCGeoItems.create_castle_atla]
geo_class = [NoruneGeoItems, MatatakiGeoItems, QueensGeoItems, MuskaGeoItems, FactoryGeoItems, DHCGeoItems]

dungeon_locations = json.loads(pkgutil.get_data(__name__, "data/atla_locations.json").decode())

prog_map = json.loads(pkgutil.get_data(__name__, "data/progressive.json").decode())

class DarkCloudWorld(World):
    """
    Dark Cloud 1
    """
    game = dc1_name
    required_client_version = (0, 6, 5)
    options_dataclass = Options.DarkCloudOptions
    options: Options.DarkCloudOptions
    topology_present = True
    web = DarkCloudWeb()

    glitches_item_name = JunkDrawer.glitch_name

    item_name_to_id = {progressive_char_recruit_name: progressive_char_recruit_id,
                       glitches_item_name: game_id.base_id - 1}
    location_name_to_id = Location.floor_location_ids()
    item_name_to_classification = {progressive_char_recruit_name: ItemClassification.progression,
                                   glitches_item_name: ItemClassification.progression}
    filler_item_names = []

    chest_filter = None

    item_count_to_gen = 0

    progressive_item_list = {}
    for prog_item in prog_map:
        progressiveName = prog_map[prog_item]
        if progressiveName not in progressive_item_list:
            progressive_item_list[progressiveName] = []
        progressive_item_list[progressiveName].append(prog_item)

    # Parse inventory item data
    item_data = []
    item_name_to_data = {}
    reader = pkgutil.get_data(__name__, "data/item_data.csv").decode().splitlines()
    for line in reader:
        row = line.split(",")
        item_name_to_id.update({row[0]: int(row[1])})
        classification = ItemClassification(int(row[2]))
        if classification == ItemClassification.filler:
            filler_item_names.append(row[0])

        # [3]-[7] are counts if an item should be added for a given town 0-5.
        counts = []
        for i in range(3, 8):
            if row[i]:
                counts.append(int(row[i]))
            else:
                counts.append(0)

        item = ItemData(row[0], int(row[1]), classification, counts)
        item_data.append(item)
        item_name_to_data[row[0]] = item

        item_name_to_classification[row[0]] = classification

    for i in geo_class:
        item_name_to_id.update(i.ids)
        item_name_to_classification.update(i.classifications)

    for i in dungeon_locations:
        location_name_to_id.update(i)

    # Parse in the miracle chest data
    mc_data = [[], [], [], [], []]
    reader = pkgutil.get_data(__name__, "data/miracle_locations.csv").decode().splitlines()
    for line in reader:
        row = line.split(",")
        mc_data[int(row[2])].append(MiracleChest(row[0], row[1], row[2], row[3], row[4]))

    for i in mc_data:
        for j in i:
            location_name_to_id.update({str(j.name): int(j.ap_id)})

    for s in shop_locations_to_id:
        location_name_to_id.update(s)

    for f in fish_locations_to_id:
        location_name_to_id.update(f)

    origin_region_name = "Norune"

    atla_per_floor = None
    ut = False_()
    is_ut = False

    def generate_early(self) -> None:
        if getattr(self.multiworld, "generation_is_fake", False):
            self.ut = True_()
            self.is_ut = True

        self.chest_filter = OptionFilter(MiracleSanity, True)

        if self.options.idea.value > 0:
            self.options.boss_goal.value = 6
            self.options.floor_sanity.value = 2

        if self.options.progressive_chars:
            temp_items = all_chars
        else:
            temp_items = split_chars

        for prog_item in temp_items:
            progressive_name = temp_items[prog_item]
            if progressive_name not in self.progressive_item_list:
                self.progressive_item_list[progressive_name] = []
            self.progressive_item_list[progressive_name].append(prog_item)

        self.normalize_atla()

    def normalize_atla(self):
        # Atla per dungeon half.  Not doing last dungeon since the alta are already static
        atla_count = [35, 38, 54, 40, 42, 32, 32, 34, 29, 27]

        # First 2 floors of DBC start above 0 so they are guaranteed to hit the minimum the game expects.
        # SMT1 last floor has 1 to guarantee it has the one expected by the game
        self.atla_per_floor = [[6, 2, 0, 0, 0, 0],    [0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 1], [0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0],    [0, 0, 0, 0, 0]]

        for i in range(min(len(atla_count), self.options.boss_goal*2)):
            count = atla_count[i]
            ll = self.atla_per_floor[i]
            l_index = 0

            while count > 0:
                if ll[l_index] < 8:
                    r = self.random.randint(1, min(8 - ll[l_index], count))
                    ll[l_index] = ll[l_index] + r
                    count = count - r

                l_index = (l_index + 1) % len(ll)

            # print (ll, sum(ll))

    def create_items(self):
        # Static items for chest shuffle
        if self.options.miracle_sanity:
            for item in self.item_data:
                items = item.to_items(self.player, self)
                self.item_count_to_gen -= len(items)
                self.multiworld.itempool.extend(items)

        # Georama
        for i in range(self.options.boss_goal):
            items = geo_funcs[i](self.options, self.player)
            self.item_count_to_gen -= len(items)
            self.multiworld.itempool.extend(items)

        # Always add fishing rod
        self.multiworld.itempool.append(self.item_name_to_data["Fishing Rod"].to_item(self.player, self))
        self.item_count_to_gen -= 1

        # Add skipped georama parts from the first 2 towns if there is space
        # Some/All Windmill/Well 3 pieces are ignored for minimal settings with extra_char_buildings on
        items = NoruneGeoItems.create_windmill_parts(self.item_count_to_gen, self.player)
        self.item_count_to_gen -= len(items)
        self.multiworld.itempool.extend(items)
        items = MatatakiGeoItems.create_well_parts(self.item_count_to_gen, self.player)
        self.item_count_to_gen -= len(items)
        self.multiworld.itempool.extend(items)

        if self.options.gem_set:
            gems = ["Garnet", "Peridot", "Diamond", "Aquamarine", "Topaz", "Pearl",
                    "Emerald", "Amethyst", "Sapphire", "Opal", "Ruby", "Turquoise"]
            for gem in gems:
                if self.item_count_to_gen > 0:
                    self.multiworld.itempool.append(self.create_item(gem))
                    self.item_count_to_gen -= 1
                else:
                    break

        # Create useful items
        half = math.ceil(self.item_count_to_gen / 2)
        items = self.gen_useful(half)
        self.item_count_to_gen -= len(items)
        self.multiworld.itempool.extend(items)

        # Create filler from remaining item count
        items = self.gen_filler(self.item_count_to_gen)
        self.item_count_to_gen -= len(items)
        self.multiworld.itempool.extend(items)

        # Count check
        if self.item_count_to_gen > 0:
            logging.warning(f"Not enough items generated for {self.player}.")
        elif self.item_count_to_gen < 0:
            logging.warning(f"Too many items generated for {self.player}.")

    def gen_useful(self, count: int) -> list[DarkCloudItem]:
        # +x attachments will have the + number determined when created, so no need to random them here
        names = {"Attack+1": 9, "Magic+1": 7, "Fire": 8, "Ice": 8, "Thunder": 8, "Wind": 8, "Holy": 8,
                 "Antidote Amulet": 8, "Powerup Powder": 9, "Gold Bullion": 6, "Dran's Feather": 9,
                 "Dragon Slayer": 9, "Undead Buster": 9, "Sea Killer": 9, "Stone Breaker": 9, "Plant Buster": 9,
                 "Beast Buster": 9, "Sky Hunter": 9, "Metal Breaker": 9, "Mimic Breaker": 9, "Mage Slayer": 9}
        # Currently not adding fishing bait, but might if fish shuffle is added?
        bait_names = {"Carrot": 7, "Potato Cake": 4, "Poisonous Apple": 4, "Petite Fish": 7, "Evy": 7, "Prickly": 7}

        if self.options.fish_sanity.value > 0:
            names.update(bait_names)

        items = []

        for name in self.random.choices(list(names.keys()), weights=list(names.values()), k=count):
            items.append(self.item_name_to_data[name].to_item(self.player, self))

        return items

    #
    def gen_filler(self, count: int) -> list[DarkCloudItem]:
        names = {"Anti-Freeze Amulet": 4, "Anti-Curse Amulet": 4, "Anti-Goo Amulet": 4,
                 "Tasty Water": 9, "Premium Water": 6, "Bread": 8, "Cheese": 10, "Premium Chicken": 6,
                 "Antidote Drink": 7, "Holy Water": 7, "Soap": 7, "Mighty Healing": 5, "Stamina Drink": 8,
                 "Bomb": 10, "Fire Gem": 8, "Ice Gem": 8, "Thunder Gem": 8, "Wind gem": 8, "Holy Gem": 8,
                 "Throbbing Cherry": 8, "Bomb Nuts": 5, "Revival Powder": 4, "Repair Powder": 10,
                 "Treasure Chest Key": 6, "Auto-Repair Powder": 4 }

        items = []

        for name in self.random.choices(list(names.keys()), weights=list(names.values()), k=count):
            items.append(self.item_name_to_data[name].to_item(self.player, self))

        return items

    # Set up progressive items
    def collect_item(self, state: "CollectionState", item: "Item", remove: bool = False) -> Optional[str]:
        if not item.advancement:
            return None
        name = item.name
        if name.startswith("Progressive ") or name == "Matataki River":
            if self.options.progressive_chars and \
                    (name.startswith("Progressive Player") or name.startswith("Progressive Cacao") or
                     name.startswith("Progressive King") or name.startswith("Progressive 3")):
                return super(DarkCloudWorld, self).collect_item(state, item, remove)

            prog_table = self.progressive_item_list[name]
            if remove:
                for item_name in reversed(prog_table):
                    if state.has(item_name, item.player):
                        return item_name
            else:
                for item_name in prog_table:
                    if not state.has(item_name, item.player):
                        return item_name

        return super(DarkCloudWorld, self).collect_item(state, item, remove)

    def shop_locations(self, towns: list[Region]):
        if self.options.shop_sanity.value == 0:
            return

        # Considered making a dict of town to shop data but this works...
        # Item ID breakdown: abcd. a: town, 1 indexed. b: 3 to indicate shops (0 for MCs, 1/2 for atla), c: shop index, d: location ID
        self.shop_location("Gaffer's Shop Item", 97111_1300, towns[0], Rules.r_gaffer)
        self.shop_location("Wise Owl Shop Item", 97111_2300, towns[1], Rules.r_owl)
        if self.options.boss_goal > 2:
            self.shop_location("Ruty's Shop Item", 97111_3300, towns[2], Rules.r_ruty)
            self.shop_location("Suzy's Shop Item", 97111_3310, towns[2], Rules.r_suzy)
            self.shop_location("Lana's Shop Item", 97111_3320, towns[2], Rules.r_lana)
            self.shop_location("Jack's Shop Item", 97111_3330, towns[2], Rules.r_jack)
            self.shop_location("Joker's Shop Item", 97111_3340, towns[2], Rules.r_joker)
            if self.options.boss_goal > 3:
                self.shop_location("Brooke's Shop Item", 97111_4300, towns[3], Rules.r_brooke)
                if self.options.boss_goal > 4:
                    self.shop_location("Ledan's Shop Item", 97111_5300, towns[4], Rules.r_ledan)
                    if self.options.boss_goal > 5:
                        self.shop_location("Fairy King's Item Shop Item", 97111_6300, towns[5], Rules.r_simba)
                        self.shop_location("Fairy King's Gem Shop Item", 97111_6310, towns[5], Rules.r_simba)
                        self.shop_location("Fairy King's Attachment Shop Item", 97111_6320, towns[5], Rules.r_simba)

        return

    def shop_location(self, name: str, item_id: int, town: Region, rule: Rule):
        loc1 = DarkCloudLocation(self.player, f"{name} 1", item_id, LocationProgressType.DEFAULT, town)
        loc2 = DarkCloudLocation(self.player, f"{name} 2", item_id + 1, LocationProgressType.DEFAULT, town)

        self.set_rule(loc1, rule)
        self.set_rule(loc2, rule)

        town.locations.append(loc1)
        town.locations.append(loc2)

        self.item_count_to_gen += 2

        return

    def fish_locations(self, regions: dict[str, Region]):
        if self.options.fish_sanity.value == 0:
            return

        niler = DarkCloudLocation(self.player, "Catch a Niler", 97111_0407, LocationProgressType.DEFAULT, regions["Norune"])
        gummy = DarkCloudLocation(self.player, "Catch a Gummy", 97111_0406, LocationProgressType.DEFAULT, regions["Norune"])
        nonky = DarkCloudLocation(self.player, "Catch a Nonky", 97111_0402, LocationProgressType.DEFAULT, regions["Norune"])
        gobbler = DarkCloudLocation(self.player, "Catch a Gobbler", 97111_0401, LocationProgressType.DEFAULT, regions["Norune"])

        if self.is_ut:
            self.set_rule(niler, FishRules.r_niler_fish_ut)
            self.set_rule(gummy, FishRules.r_gummy_fish_ut)
            self.set_rule(nonky, FishRules.r_gummy_fish_ut)
            self.set_rule(gobbler, FishRules.r_gobbler_fish_ut)
        else:
            self.set_rule(niler, FishRules.r_niler_fish)
            self.set_rule(gummy, FishRules.r_gummy_fish)
            self.set_rule(nonky, FishRules.r_gummy_fish)
            self.set_rule(gobbler, FishRules.r_gobbler_fish)

        regions["Norune"].locations.extend([niler, gummy, nonky, gobbler])
        self.item_count_to_gen += 4

        baku = DarkCloudLocation(self.player, "Catch a Baku Baku", 97111_0404, LocationProgressType.DEFAULT, regions["Matataki"])
        tarton = DarkCloudLocation(self.player, "Catch a Tarton", 97111_0410, LocationProgressType.DEFAULT, regions["Matataki"])
        umadakara = DarkCloudLocation(self.player, "Catch an Umadakara", 97111_0409, LocationProgressType.DEFAULT, regions["Matataki"])

        if self.is_ut:
            self.set_rule(baku, FishRules.r_baku_fish_ut)
            self.set_rule(tarton, FishRules.r_tarton_fish_ut)
            self.set_rule(umadakara, FishRules.r_umadakara_fish_ut)
        else:
            self.set_rule(baku, FishRules.r_baku_fish)
            self.set_rule(tarton, FishRules.r_tarton_fish)
            self.set_rule(umadakara, FishRules.r_umadakara_fish)

        regions["Matataki"].locations.extend([baku, tarton, umadakara])
        self.item_count_to_gen += 3

        if self.options.boss_goal > 2:
            if self.options.fish_sanity.value >= 2:
                mardan = DarkCloudLocation(self.player, "Catch a Mardan Garayan", 97111_0405,
                                           LocationProgressType.DEFAULT, regions["Matataki"])
                if self.is_ut:
                    self.set_rule(mardan, FishRules.r_mardan_fish_ut)
                else:
                    self.set_rule(mardan, FishRules.r_mardan_fish)
                regions["Matataki"].locations.append(mardan)
                self.item_count_to_gen += 1


            ocean_region = Region("Ocean Fish", self.player, self.multiworld)
            ocean_fish = [("Catch a Hama Hama", 97111_0413), ("Catch a Kaji", 97111_0403),
                          ("Catch a Piccoly", 97111_0411), ("Catch a Bon", 97111_0412), ("Catch a Bobo", 97111_0400)]

            if self.is_ut:
                ocean_rule = FishRules.r_ocean_fish_ut
            else:
                ocean_rule = FishRules.r_ocean_fish

            for fish in ocean_fish:
                ocean_region.locations.append(DarkCloudLocation(self.player, fish[0], fish[1],
                                        LocationProgressType.DEFAULT, ocean_region))

            self.create_entrance(regions["Queens"], ocean_region, ocean_rule)
            self.multiworld.regions.append(ocean_region)
            self.item_count_to_gen += len(ocean_fish)

            if self.options.boss_goal > 3:
                if self.options.fish_sanity.value >= 2:
                    baron = DarkCloudLocation(self.player, "Catch a Baron Garayan", 97111_0417,
                                               LocationProgressType.DEFAULT, regions["Matataki"])
                    if self.is_ut:
                        self.set_rule(baron, FishRules.r_baron_fish_ut)
                    else:
                        self.set_rule(baron, FishRules.r_baron_fish)
                    regions["Matataki"].locations.append(baron)
                    self.item_count_to_gen += 1

                oasis_region = Region("Oasis Fish", self.player, self.multiworld)
                desert_fish = [("Catch a Den", 97111_0415), ("Catch a Heela", 97111_0416),
                               ("Catch a Negie", 97111_0414)]
                if self.is_ut:
                    desert_rule = FishRules.r_desert_fish_ut
                else:
                    desert_rule = FishRules.r_desert_fish

                for fish in desert_fish:
                    oasis_region.locations.append(DarkCloudLocation(self.player, fish[0], fish[1],
                                                                    LocationProgressType.DEFAULT, oasis_region))

                self.create_entrance(regions["Muska"], oasis_region, desert_rule)
                self.multiworld.regions.append(oasis_region)
                self.item_count_to_gen += len(desert_fish)

        return

    def create_regions(self):
        regions: typing.Dict[str, Region] = {}

        # Towns
        norune = Region("Norune", self.player, self.multiworld)
        matataki = Region("Matataki", self.player, self.multiworld)
        queens = Region("Queens", self.player, self.multiworld)
        muska = Region("Muska", self.player, self.multiworld)
        factory = Region("Factory", self.player, self.multiworld)
        dhc = Region("DHC", self.player, self.multiworld)

        # Dungeons
        dbc1 = Region("DBC1", self.player, self.multiworld)
        dbc2 = Region("DBC2", self.player, self.multiworld)
        wof1 = Region("WOF1", self.player, self.multiworld)
        wof2 = Region("WOF2", self.player, self.multiworld)
        sw1 = Region("SW1", self.player, self.multiworld)
        sw2 = Region("SW2", self.player, self.multiworld)
        smt1 = Region("SMT1", self.player, self.multiworld)
        smt2 = Region("SMT2", self.player, self.multiworld)
        ms1 = Region("MS1", self.player, self.multiworld)
        ms2 = Region("MS2", self.player, self.multiworld)
        got = Region("GOT", self.player, self.multiworld)

        towns = [norune, matataki, queens, muska, factory, dhc]
        dungeons = [dbc1, dbc2, wof1, wof2, sw1, sw2, smt1, smt2, ms1, ms2, got]

        for town in towns:
            regions[town.name] = town

        for dungeon in dungeons:
            regions[dungeon.name] = dungeon

        # Create dungeon locations. Only add locations for the relevant dungeons
        for i in range(min(len(dungeons), self.options.boss_goal * 2)):
            dun = dungeons[i]
            dun_locs = dungeon_locations[i]
            self.item_count_to_gen += len(dun_locs)

            # Create locations, then add to the dungeons
            for key in dun_locs:
                loc = DarkCloudLocation(self.player, key, dun_locs[key], LocationProgressType.DEFAULT, dun)
                dun.locations.append(loc)

        # Create miracle chest locations
        if self.options.miracle_sanity:
            # Regions for chests requiring local character
            xiao_chests = Region("Xiao-Locked Chests", self.player, self.multiworld)
            goro_chests = Region("Goro-Locked Chests", self.player, self.multiworld)
            ruby_chests = Region("Ruby-Locked Chests", self.player, self.multiworld)
            ungaga_chests = Region("Ungaga-Locked Chests", self.player, self.multiworld)
            osmond_chests = Region("Osmond-Locked Chests", self.player, self.multiworld)

            chest_regions = [xiao_chests, goro_chests, ruby_chests, ungaga_chests, osmond_chests]
            for chest_region in chest_regions:
                regions[chest_region.name] = chest_region

            for i in range(min(5, int(self.options.boss_goal))):
                mcs = self.mc_data[i]
                self.item_count_to_gen += len(mcs)
                for chest in mcs:
                    if chest.req_char:
                        loc = DarkCloudLocation(self.player, str(chest.name), int(chest.ap_id),
                                                LocationProgressType.DEFAULT, chest_regions[i])
                        chest_regions[i].locations.append(loc)
                    else:
                        loc = DarkCloudLocation(self.player, str(chest.name), int(chest.ap_id),
                                                LocationProgressType.DEFAULT, towns[i])
                        towns[i].locations.append(loc)

                    if not chest.req_geo:
                        self.set_rule(loc, True_())
                    else:
                        self.set_rule(loc, HasAll(*chest.req_geo))

        # Create shop locations if enabled
        self.shop_locations(towns)
        # Create fish locations if enabled
        self.fish_locations(regions)
        self.item_count_to_gen += Location.floor_locations(self.player, self.options.boss_goal.value,
                                                           self.options.floor_sanity.value, self.options.idea.value,
                                                           dungeons)

        # Connect Regions and set rules
        self.create_entrance(regions["Norune"], regions["Matataki"], (self.ut & Rules.r_xiao_available_only_ut) | Rules.r_xiao_available_only)
        self.create_entrance(regions["Matataki"], regions["Queens"], (self.ut & Rules.r_goro_available_only_ut) | Rules.r_goro_available_only)
        self.create_entrance(regions["Queens"], regions["Muska"], Rules.r_ruby_available_only)
        self.create_entrance(regions["Muska"], regions["Factory"], Rules.r_ungaga_available_only)
        self.create_entrance(regions["Factory"], regions["DHC"], Rules.r_dhc_available & Rules.r_osmond_available_only)

        self.create_entrance(regions["Norune"], regions["DBC1"])
        self.create_entrance(regions["Norune"], regions["DBC2"], (self.ut & Rules.r_xiao_available_only_ut) | Rules.r_xiao_available_only)

        self.create_entrance(regions["Matataki"], regions["WOF1"])
        self.create_entrance(regions["Matataki"], regions["WOF2"], (self.ut & Rules.r_goro_available_ut) | Rules.r_goro_available)

        self.create_entrance(regions["Queens"], regions["SW1"], (Rules.chest_shuffle_off | Rules.r_goro_items))
        self.create_entrance(regions["Queens"], regions["SW2"], Rules.r_ruby_available)

        self.create_entrance(regions["Muska"], regions["SMT1"], (Rules.chest_shuffle_off | Rules.r_ruby_items))
        self.create_entrance(regions["Muska"], regions["SMT2"], Rules.r_ungaga_available)

        self.create_entrance(regions["Factory"], regions["MS1"], (Rules.chest_shuffle_off | Rules.r_ungaga_items))
        self.create_entrance(regions["Factory"], regions["MS2"], Rules.r_osmond_available)

        self.create_entrance(regions["DHC"], regions["GOT"], (Rules.chest_shuffle_off | Rules.r_osmond_items))

        if self.options.miracle_sanity:
            self.create_entrance(regions["Norune"], regions["Xiao-Locked Chests"],
                                 (self.ut & Rules.r_xiao_available_only_ut) | Rules.r_xiao_available_only)
            self.create_entrance(regions["Matataki"], regions["Goro-Locked Chests"],
                                 (self.ut & Rules.r_goro_available_only_ut) | Rules.r_goro_available)
            self.create_entrance(regions["Queens"], regions["Ruby-Locked Chests"],
                                 (self.ut & Rules.r_ruby_available_only) | Rules.r_ruby_available)
            self.create_entrance(regions["Muska"], regions["Ungaga-Locked Chests"],
                                 (self.ut & Rules.r_ungaga_available_only) | Rules.r_ungaga_available)
            self.create_entrance(regions["Factory"], regions["Osmond-Locked Chests"],
                                 (self.ut & Rules.r_osmond_available_only) | Rules.r_osmond_available)

        self.multiworld.regions.extend(regions.values())

    def set_rules(self):
        # Set up completion goal
        self.set_completion_rule(Rules.get_completion_rule(self.options))

    def create_item(self, name:str) -> DarkCloudItem:
        classification = self.item_name_to_classification[name]
        return DarkCloudItem(name, classification, self.item_name_to_id[name], self.player)

    def get_filler_item_name(self) -> str:
        return self.filler_item_names[self.random.randint(0, len(self.filler_item_names) - 1)]

    def fill_slot_data(self) -> Mapping[str, Any]:
        slot_data = {
            "options": {
                "goal": self.options.boss_goal.value,
                "all_bosses": self.options.all_bosses.value,
                "memory_count": self.options.memory_count.value,
                "open_dungeon": self.options.open_dungeon.value,
                "progressive_chars": self.options.progressive_chars.value,
                "starter_weapons": self.options.starter_weapons.value,
                "abs_multiplier": self.options.abs_multiplier.value,
                "attach_multiplier": self.options.attach_multiplier.value,
                "attach_mult_config": self.options.attach_mult_config.value,
                "auto_build": self.options.auto_build.value,
                "miracle_sanity": self.options.miracle_sanity.value,
                "shop_sanity": self.options.shop_sanity.value,
                "fish_sanity": self.options.fish_sanity.value,
                "floor_sanity": self.options.floor_sanity.value,
                "death_link": self.options.death_link.value,
                "toan_name": self.options.toan_name.value,
                "xiao_name": self.options.xiao_name.value,
                "goro_name": self.options.goro_name.value,
                "ruby_name": self.options.ruby_name.value,
                "ungaga_name": self.options.ungaga_name.value,
                "osmond_name": self.options.osmond_name.value,
                "apf": self.atla_per_floor,
            },
        }

        return slot_data