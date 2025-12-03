import json
import pkgutil
import typing
from typing import Mapping, Any, Optional

from BaseClasses import Region, LocationProgressType, Item, CollectionState, ItemClassification
from worlds.AutoWorld import World, WebWorld
from worlds.dc1.data import (NoruneGeoItems, MatatakiGeoItems, QueensGeoItems,
                             MuskaGeoItems, FactoryGeoItems, DHCGeoItems)
from worlds.generic.Rules import set_rule
from . import Rules
from .Items import DarkCloudItem, ItemData
from .Location import DarkCloudLocation
from .Options import DarkCloudOptions
from .data.MiracleChest import MiracleChest
from .game_id import dc1_name

geo_funcs = [NoruneGeoItems.create_norune_atla, MatatakiGeoItems.create_matataki_atla,
             QueensGeoItems.create_queens_atla, MuskaGeoItems.create_muska_atla,
             FactoryGeoItems.create_factory_atla, DHCGeoItems.create_castle_atla]
geo_class = [NoruneGeoItems, MatatakiGeoItems, QueensGeoItems, MuskaGeoItems, FactoryGeoItems, DHCGeoItems]

dungeon_locations = json.loads(pkgutil.get_data(__name__, "data/atla_locations.json").decode())

# TODO webworld implementation as we get closer to completion.
class DarkCloudWeb(WebWorld):
    theme = "jungle"
    bug_report_page = ""


class DarkCloudWorld(World):
    """
    Dark Cloud 1
    """
    game = dc1_name
    required_client_version = (0, 6, 1)
    options_dataclass = DarkCloudOptions
    options: DarkCloudOptions
    topology_present = True
    web = DarkCloudWeb()

    item_name_to_id = {}
    location_name_to_id = {}

    # Parse inventory item data
    item_data = [[],[],[],[],[]]
    reader = pkgutil.get_data(__name__, "data/item_data.csv").decode().splitlines()
    for line in reader:
        row = line.split(",")
        item_name_to_id.update({row[0]: int(row[1])})
        # TODO cleaner way to do this
        # [3]-[7] are counts if an item should be added for a given town 0-5.
        if row[3]:
            item_data[0].append(ItemData(row[0], int(row[1]), int(row[2]), int(row[3])))
        if row[4]:
            item_data[1].append(ItemData(row[0], int(row[1]), int(row[2]), int(row[4])))
        if row[5]:
            item_data[2].append(ItemData(row[0], int(row[1]), int(row[2]), int(row[5])))
        if row[6]:
            item_data[3].append(ItemData(row[0], int(row[1]), int(row[2]), int(row[6])))
        if row[7]:
            item_data[4].append(ItemData(row[0], int(row[1]), int(row[2]), int(row[7])))

    for i in geo_class:
        item_name_to_id.update(i.ids)

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
            location_name_to_id.update({str(j.get_name()): int(j.get_ap_id())})
    location_name_to_id.update({"Mushroom House inside chest (sundew)": 971112075})

    origin_region_name = "Norune"

    def create_items(self):
        for i in range(self.options.boss_goal):
            self.multiworld.itempool.extend(geo_funcs[i](self.options, self.player))

        if self.options.miracle_sanity:
            for i in range(min(5, int(self.options.boss_goal))):
                for item in self.item_data[i]:
                    self.multiworld.itempool.extend(item.to_items(self.player))
            if self.options.sundew_chest:
                self.multiworld.itempool.append(DarkCloudItem("Sundew", ItemClassification.progression, 971111225, self.player))

    # Set up progressive items
    def collect_item(self, state: "CollectionState", item: "Item", remove: bool = False) -> Optional[str]:
        if not item.advancement:
            return None
        name = item.name
        if name.startswith("Progressive "):
            prog_table = Items.progressive_item_list[name]
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
        sr1 = Region("SR1", self.player, self.multiworld)
        sr2 = Region("SR2", self.player, self.multiworld)
        smt1 = Region("SMT1", self.player, self.multiworld)
        smt2 = Region("SMT2", self.player, self.multiworld)
        ms1 = Region("MS1", self.player, self.multiworld)
        ms2 = Region("MS2", self.player, self.multiworld)
        got = Region("GOT", self.player, self.multiworld)

        towns = [norune, matataki, queens, muska, factory, dhc]
        dungeons = [dbc1, dbc2, wof1, wof2, sr1, sr2, smt1, smt2, ms1, ms2, got]

        for town in towns:
            regions[town.name] = town

        for dungeon in dungeons:
            regions[dungeon.name] = dungeon

        # Only add locations for the relevant dungeons
        for i in range(min(len(dungeons), self.options.boss_goal * 2)):
            dun = dungeons[i]
            dun_locs = dungeon_locations[i]

            # Create locations, then add to the dungeons
            for key in dun_locs:
                loc = DarkCloudLocation(self.player, key, dun_locs[key], LocationProgressType.DEFAULT, dun)
                dun.locations.append(loc)

        if self.options.miracle_sanity:
            for i in range(min(5, int(self.options.boss_goal))):
                mcs = self.mc_data[i]
                for chest in mcs:
                    loc = DarkCloudLocation(self.player, str(chest.name), int(chest.ap_id), LocationProgressType.DEFAULT, towns[i])
                    loc.access_rule = lambda state, a=chest.req_char, b=chest.req_geo: Rules.chest_test(state, self.player, a, b)
                    towns[i].locations.append(loc)
            # Location for the sundew chest
            if self.options.sundew_chest:
                loc = DarkCloudLocation(self.player, "Mushroom House inside chest (sundew)", 971112075,
                                  LocationProgressType.DEFAULT, matataki)
                loc.access_rule = lambda state: Rules.chest_test(state, self.player, "goro", ["Mushroom House"])
                matataki.locations.append(loc)

        # Connect Regions
        def create_connection(from_region: str, to_region: str):
            regions[from_region].connect(regions[to_region])

        create_connection("Norune", "Matataki")
        create_connection("Norune", "Queens")
        create_connection("Norune", "Muska")
        create_connection("Norune", "Factory")
        create_connection("Norune", "DHC")

        create_connection("Norune", "DBC1")
        create_connection("Norune", "DBC2")

        create_connection("Matataki", "WOF1")
        create_connection("Matataki", "WOF2")

        create_connection("Queens", "SR1")
        create_connection("Queens", "SR2")

        create_connection("Muska", "SMT1")
        create_connection("Muska", "SMT2")

        create_connection("Factory", "MS1")
        create_connection("Factory", "MS2")

        create_connection("DHC", "GOT")

        self.multiworld.regions.extend(towns)
        self.multiworld.regions.extend(dungeons)

    def set_rules(self):

        set_rule(self.multiworld.get_entrance("Norune -> DBC1", self.player), lambda state: True)
        set_rule(self.multiworld.get_entrance("Norune -> DBC2", self.player),
                 lambda state: Rules.xiao_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Norune -> Matataki", self.player),
                 lambda state: Rules.xiao_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Matataki -> WOF1", self.player),
                 lambda state: Rules.xiao_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Matataki -> WOF2", self.player),
                 lambda state: Rules.goro_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Norune -> Queens", self.player),
                 lambda state: Rules.goro_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Queens -> SR1", self.player),
                 lambda state: Rules.goro_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Queens -> SR2", self.player),
                 lambda state: Rules.ruby_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Norune -> Muska", self.player),
                 lambda state: Rules.ruby_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Muska -> SMT1", self.player),
                 lambda state: Rules.ruby_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Muska -> SMT2", self.player),
                 lambda state: Rules.ungaga_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Norune -> Factory", self.player),
                 lambda state: Rules.ungaga_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Factory -> MS1", self.player),
                 lambda state: Rules.ungaga_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Factory -> MS2", self.player),
                 lambda state: Rules.osmond_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Norune -> DHC", self.player),
                 lambda state: Rules.got_accessible(state, self.player))
        set_rule(self.multiworld.get_entrance("DHC -> GOT", self.player),
                 lambda state: Rules.got_accessible(state, self.player))

        # Set up completion goal
        match self.options.boss_goal:
            case 2:
                if self.options.all_bosses:
                    self.multiworld.completion_condition[self.player] = lambda state: Rules.utan_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options) and \
                                                                                      Rules.dran_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options)
                else:
                    self.multiworld.completion_condition[self.player] = lambda state: Rules.utan_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options)
            case 3:
                if self.options.all_bosses:
                    self.multiworld.completion_condition[self.player] = lambda state: Rules.saia_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options) and \
                                                                                      Rules.utan_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options) and \
                                                                                      Rules.dran_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options)
                else:
                    self.multiworld.completion_condition[self.player] = lambda state: Rules.saia_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options)
            case 4:
                if self.options.all_bosses:
                    self.multiworld.completion_condition[self.player] = lambda state: Rules.curse_accessible(state,
                                                                                                             self.player,
                                                                                                            self.options) and \
                                                                                      Rules.saia_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options) and \
                                                                                      Rules.utan_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options) and \
                                                                                      Rules.dran_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options)
                else:
                    self.multiworld.completion_condition[self.player] = lambda state: Rules.curse_accessible(state,
                                                                                                             self.player,
                                                                                                            self.options)
            case 5:
                if self.options.all_bosses:
                    self.multiworld.completion_condition[self.player] = lambda state: Rules.joe_accessible(state,
                                                                                                           self.player,
                                                                                                            self.options) and \
                                                                                      Rules.curse_accessible(state,
                                                                                                             self.player,
                                                                                                            self.options) and \
                                                                                      Rules.saia_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options) and \
                                                                                      Rules.utan_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options) and \
                                                                                      Rules.dran_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options)
                else:
                    self.multiworld.completion_condition[self.player] = lambda state: Rules.joe_accessible(state,
                                                                                                           self.player,
                                                                                                            self.options)
            case 6:
                if self.options.all_bosses:
                    self.multiworld.completion_condition[self.player] = lambda state: Rules.genie_accessible(state,
                                                                                                             self.player,
                                                                                                            self.options) and \
                                                                                      Rules.joe_accessible(state,
                                                                                                           self.player,
                                                                                                            self.options) and \
                                                                                      Rules.curse_accessible(state,
                                                                                                             self.player,
                                                                                                            self.options) and \
                                                                                      Rules.saia_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options) and \
                                                                                      Rules.utan_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options) and \
                                                                                      Rules.dran_accessible(state,
                                                                                                            self.player,
                                                                                                            self.options)
                else:
                    self.multiworld.completion_condition[self.player] = lambda state: Rules.genie_accessible(state,
                                                                                                             self.player,
                                                                                                             self.options)

    def fill_slot_data(self) -> Mapping[str, Any]:
        slot_data = {
            "options": {
                "goal": self.options.boss_goal.value,
                "all_bosses": self.options.all_bosses.value,
                "open_dungeon": self.options.open_dungeon.value,
                "starter_weapons": self.options.starter_weapons.value,
                "abs_multiplier": self.options.abs_multiplier.value,
                "auto_build": self.options.auto_build.value,
                "miracle_sanity": self.options.miracle_sanity.value,
                "sundew_chest": self.options.sundew_chest.value,
            },
        }

        return slot_data
