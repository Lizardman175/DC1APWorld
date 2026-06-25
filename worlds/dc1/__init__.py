import json
import logging
import math
import pkgutil
import typing
from typing import Mapping, Any, Optional

from BaseClasses import Region, LocationProgressType, Item, CollectionState, ItemClassification
from rule_builder.options import OptionFilter
from rule_builder.rules import HasAll, True_, False_
from worlds.AutoWorld import World, WebWorld
from .JunkDrawer import dark_genie_id, progressive_char_recruit_name, progressive_char_recruit_id

from .data import (NoruneGeoItems, MatatakiGeoItems, QueensGeoItems,
                   MuskaGeoItems, FactoryGeoItems, DHCGeoItems)
from .Items import DarkCloudItem, ItemData
from .Location import DarkCloudLocation
from .Options import DarkCloudOptions, MiracleSanity
from .data.MiracleChest import MiracleChest
from .data.Progressive import all_chars, split_chars
from .game_id import dc1_name
from .rules import Rules

geo_funcs = [NoruneGeoItems.create_norune_atla, MatatakiGeoItems.create_matataki_atla,
             QueensGeoItems.create_queens_atla, MuskaGeoItems.create_muska_atla,
             FactoryGeoItems.create_factory_atla, DHCGeoItems.create_castle_atla]
geo_class = [NoruneGeoItems, MatatakiGeoItems, QueensGeoItems, MuskaGeoItems, FactoryGeoItems, DHCGeoItems]

dungeon_locations = json.loads(pkgutil.get_data(__name__, "data/atla_locations.json").decode())

prog_map = json.loads(pkgutil.get_data(__name__, "data/progressive.json").decode())

# TODO webworld implementation as we get closer to completion.
class DarkCloudWeb(WebWorld):
    theme = "jungle"
    bug_report_page = ""


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

    item_name_to_id = {"Dark Genie": dark_genie_id, progressive_char_recruit_name: progressive_char_recruit_id}
    location_name_to_id = {"Dark Genie": dark_genie_id, }
    item_name_to_classification = {progressive_char_recruit_name: ItemClassification.progression}
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

    origin_region_name = "Norune"

    atla_per_floor = None
    ut = False_()

    def generate_early(self) -> None:
        if hasattr(self.multiworld, "generation_is_fake"):
            self.ut = True_()

        self.chest_filter = OptionFilter(MiracleSanity, True)

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

        # Create Well 3 parts if item count remains above 0
        # Some/All Well 3 pieces are ignored for minimal settings with extra_char_buildings on
        items = MatatakiGeoItems.create_well_parts(self.item_count_to_gen, self.player)
        self.item_count_to_gen -= len(items)
        self.multiworld.itempool.extend(items)

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
        names = ["Attack+1", "Magic+1", "Fire", "Ice", "Thunder", "Wind", "Holy", "Antidote Amulet", "Powerup Powder",
                 "Gold Bullion", "Dran's Feather", "Dragon Slayer", "Undead Buster", "Sea Killer", "Stone Breaker",
                 "Plant Buster", "Beast Buster", "Sky Hunter", "Metal Breaker", "Mimic Breaker", "Mage Slayer"]
        items = []

        for i in range(count):
            rand = self.random.randint(0, len(names)-1)
            item = self.item_name_to_data[names[rand]].to_item(self.player, self)
            items.append(item)

        return items

    #
    def gen_filler(self, count: int) -> list[DarkCloudItem]:
        names = ["Anti-Freeze Amulet", "Anti-Curse Amulet", "Anti-Goo Amulet",
                 "Tasty Water", "Premium Water", "Bread", "Premium Chicken", "Stamina Drink",
                 "Antidote Drink", "Holy Water", "Soap", "Mighty Healing", "Cheese", "Bomb", "Fire Gem",
                 "Ice Gem", "Thunder Gem", "Wind gem", "Holy Gem", "Throbbing Cherry", "Bomb Nuts",
                 "Revival Powder", "Repair Powder", "Treasure Chest Key", "Auto-Repair Powder", ]
        # Currently not adding fishing bait, but might if fish shuffle is added?
        bait_names = ["Carrot", "Potato Cake", "Minon", "Battan", "Petite Fish", "Evy", "Mimi", "Prickly",
                      "Gooey Peach", "Poisonous Apple", "Mellow Banana", ]
        items = []

        for i in range(count):
            rand = self.random.randint(0, len(names)-1)
            item = self.item_name_to_data[names[rand]].to_item(self.player, self)
            items.append(item)

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

        # Sometimes players kill the DG before the other bosses then have to refight the genie.  This will allow the
        # client to acknowledge the genie kill in that situation.
        if self.options.all_bosses and self.options.boss_goal == 6:
            loc = DarkCloudLocation(self.player, "Dark Genie", dark_genie_id, LocationProgressType.DEFAULT, got)
            item = DarkCloudItem("Dark Genie", ItemClassification.progression, dark_genie_id, self.player)
            loc.place_locked_item(item)
            self.set_rule(loc, Rules.get_completion_rule(self.options))
            got.locations.append(loc)

        # Connect Regions and set rules
        self.create_entrance(regions["Norune"], regions["Matataki"], (self.ut & Rules.r_xiao_available_only_ut) | Rules.r_xiao_available_only)
        self.create_entrance(regions["Matataki"], regions["Queens"], (self.ut & Rules.r_goro_available_only_ut) | Rules.r_goro_available)
        self.create_entrance(regions["Queens"], regions["Muska"], (self.ut & Rules.r_ruby_available_only) | Rules.r_ruby_available)
        self.create_entrance(regions["Muska"], regions["Factory"], (self.ut & Rules.r_ungaga_available_only) | Rules.r_ungaga_available)
        self.create_entrance(regions["Factory"], regions["DHC"], Rules.r_dhc_available & ((self.ut & Rules.r_osmond_available_only) | Rules.r_osmond_available))

        self.create_entrance(regions["Norune"], regions["DBC1"])
        self.create_entrance(regions["Norune"], regions["DBC2"], (self.ut & Rules.r_xiao_available_only_ut) | Rules.r_xiao_available_only)

        self.create_entrance(regions["Matataki"], regions["WOF1"])
        self.create_entrance(regions["Matataki"], regions["WOF2"], (self.ut & Rules.r_goro_available_only_ut) | Rules.r_goro_available)

        self.create_entrance(regions["Queens"], regions["SW1"])
        self.create_entrance(regions["Queens"], regions["SW2"], (self.ut & Rules.r_ruby_available_only) | Rules.r_ruby_available)

        self.create_entrance(regions["Muska"], regions["SMT1"])
        self.create_entrance(regions["Muska"], regions["SMT2"], (self.ut & Rules.r_ungaga_available_only) | Rules.r_ungaga_available)

        self.create_entrance(regions["Factory"], regions["MS1"])
        self.create_entrance(regions["Factory"], regions["MS2"], (self.ut & Rules.r_osmond_available_only) | Rules.r_osmond_available)

        self.create_entrance(regions["DHC"], regions["GOT"])

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