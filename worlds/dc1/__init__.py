import json
import pkgutil
import typing
from typing import Mapping, Any, Optional

from BaseClasses import Region, LocationProgressType, Item, CollectionState, ItemClassification
from worlds.AutoWorld import World, WebWorld
from worlds.generic.Rules import set_rule
from .JunkDrawer import dark_genie_id, progressive_char_recruit_name, progressive_char_recruit_id

from .data import (NoruneGeoItems, MatatakiGeoItems, QueensGeoItems,
                   MuskaGeoItems, FactoryGeoItems, DHCGeoItems)
from .Items import DarkCloudItem, ItemData
from .Location import DarkCloudLocation
from .Options import DarkCloudOptions
from .data.MiracleChest import MiracleChest
from .data.Progressive import all_chars, split_chars
from .game_id import dc1_name
from .rules import ChestRules
from .rules.BossRules import BossRules
from .rules.BossRulesItems import BossRulesItems
from .rules.CharRules import CharRules
from .rules.CharRulesInterface import CharRulesInterface
from .rules.CharRulesItems import CharRulesItems
from .rules.CharRulesUT import CharRulesUT

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
    required_client_version = (0, 6, 1)
    options_dataclass = Options.DarkCloudOptions
    options: Options.DarkCloudOptions
    topology_present = True
    web = DarkCloudWeb()

    item_name_to_id = {"Dark Genie": dark_genie_id, }
    location_name_to_id = {"Dark Genie": dark_genie_id, }
    item_name_to_classification = {}
    filler_item_names = []

    char_rules: CharRulesInterface = None
    boss_rules: BossRules = None

    progressive_item_list = {}
    for prog_item in prog_map:
        progressiveName = prog_map[prog_item]
        if progressiveName not in progressive_item_list:
            progressive_item_list[progressiveName] = []
        progressive_item_list[progressiveName].append(prog_item)

    # Parse inventory item data
    item_data = [[],[],[],[],[]]
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

        item_data[0].append(ItemData(row[0], int(row[1]), classification, counts))

        item_name_to_classification[row[0]] = classification

    item_name_to_id.update({progressive_char_recruit_name: progressive_char_recruit_id})

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

    # Floors will at a minimum get +1 each.  -1 is used so the rare 0 atla floor is possible
    atla_per_floor = [[6, 2, -1, -1, -1, -1], [-1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1],
                      [0, -1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1, -1, -1],
                      [0, -1, -1, -1, -1, -1, 0], [-1, -1, -1, -1, -1, -1, -1],
                      [-1, -1, -1, -1, -1, -1], [-1, -1, -1, -1, -1]]

    def generate_early(self) -> None:
        if hasattr(self.multiworld, "generation_is_fake"):
            self.char_rules = CharRulesUT()
        elif self.options.miracle_sanity:
            self.char_rules = CharRulesItems()
        else:
            self.char_rules = CharRules()

        if self.options.miracle_sanity:
            self.boss_rules = BossRulesItems()
        else:
            self.boss_rules = BossRules()
        self.boss_rules.set_char_rules(self.char_rules)
        # Don't add any generation actions before this line!  Need to determine rule classes first

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
        atla_count = [39, 43, 61, 46, 48, 39, 38, 41, 35, 32]

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
        for i in range(self.options.boss_goal):
            self.multiworld.itempool.extend(geo_funcs[i](self.options, self.player))

        if self.options.miracle_sanity:
            for i in range(min(5, int(self.options.boss_goal))):
                for item in self.item_data[i]:
                    self.multiworld.itempool.extend(item.to_items(self.player, self))

    # Set up progressive items
    def collect_item(self, state: "CollectionState", item: "Item", remove: bool = False) -> Optional[str]:
        if not item.advancement:
            return None
        name = item.name
        if name.startswith("Progressive ") or name == "Matataki River":
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
                    loc = DarkCloudLocation(self.player, str(chest.name), int(chest.ap_id),
                                            LocationProgressType.DEFAULT, towns[i])
                    if not chest.req_char:
                        if not chest.req_geo:
                            loc.access_rule = lambda state: True
                        else:
                            loc.access_rule = lambda state, geo=chest.req_geo: state.has_all(geo, self.player)
                    else:
                        if chest.req_char == "xiao":
                            if hasattr(self.multiworld, "generation_is_fake"):
                                if chest.req_geo:
                                    loc.access_rule = lambda state, geo=chest.req_geo: \
                                        ChestRules.xiao_available_only_ut(state, self.player) and state.has_all(geo, self.player)
                                else:
                                    loc.access_rule = lambda state: ChestRules.xiao_available_only_ut(state, self.player)
                            else:
                                if chest.req_geo:
                                    loc.access_rule = lambda state, geo=chest.req_geo: \
                                        ChestRules.xiao_available_only(state, self.player) and state.has_all(geo, self.player)
                                else:
                                    loc.access_rule = lambda state: ChestRules.xiao_available_only(state, self.player)
                        elif chest.req_char == "goro":
                            if hasattr(self.multiworld, "generation_is_fake"):
                                if chest.req_geo:
                                    loc.access_rule = lambda state, geo=chest.req_geo: \
                                        ChestRules.goro_available_only_ut(state, self.player) and state.has_all(geo, self.player)
                                else:
                                    loc.access_rule = lambda state: ChestRules.goro_available_only_ut(state, self.player)
                            else:
                                if chest.req_geo:
                                    loc.access_rule = lambda state, geo=chest.req_geo: \
                                        ChestRules.goro_available_only(state, self.player) and state.has_all(geo, self.player)
                                else:
                                    loc.access_rule = lambda state: ChestRules.goro_available_only(state, self.player)
                        elif chest.req_char == "ruby":
                            if chest.req_geo:
                                loc.access_rule = lambda state, geo=chest.req_geo: \
                                    ChestRules.ruby_available_only(state, self.player) and state.has_all(geo, self.player)
                            else:
                                loc.access_rule = lambda state: ChestRules.ruby_available_only(state, self.player)
                        elif chest.req_char == "ungaga":
                            if chest.req_geo:
                                loc.access_rule = lambda state, geo=chest.req_geo: \
                                    ChestRules.ungaga_available_only(state, self.player) and state.has_all(geo, self.player)
                            else:
                                loc.access_rule = lambda state: ChestRules.ungaga_available_only(state, self.player)
                        # Some items have Osmond listed but he doesn't currently have any special requirements beyond the region
                        # so we need to handle ignoring him with these 2 cases:
                        elif chest.req_geo:
                            loc.access_rule = lambda state, geo=chest.req_geo: state.has_all(geo, self.player)
                        else:
                            loc.access_rule = lambda state: True

                    towns[i].locations.append(loc)

        # Sometimes players kill the DG before the other bosses then have to refight the genie.  This will allow the
        # client to acknowledge the genie kill in that situation.
        if self.options.all_bosses and self.options.boss_goal == 6:
            loc = DarkCloudLocation(self.player, "Dark Genie", dark_genie_id, LocationProgressType.DEFAULT, got)
            item = DarkCloudItem("Dark Genie", ItemClassification.progression, dark_genie_id, self.player)
            loc.place_locked_item(item)
            loc.access_rule = lambda state: self.boss_rules.genie_access(state, self.player, self.options.genie_pieces.value)
            got.locations.append(loc)

        # Connect Regions
        def create_connection(from_region: str, to_region: str):
            regions[from_region].connect(regions[to_region])

        create_connection("Norune", "Matataki")
        create_connection("Matataki", "Queens")
        create_connection("Queens", "Muska")
        create_connection("Muska", "Factory")
        create_connection("Factory", "DHC")

        create_connection("Norune", "DBC1")
        create_connection("Norune", "DBC2")

        create_connection("Matataki", "WOF1")
        create_connection("Matataki", "WOF2")

        create_connection("Queens", "SW1")
        create_connection("Queens", "SW2")

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
                 lambda state: self.char_rules.xiao_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Norune -> Matataki", self.player),
                 lambda state: self.char_rules.xiao_available(state, self.player))
        set_rule(self.multiworld.get_entrance("Matataki -> WOF1", self.player),
                lambda state: True)

        set_rule(self.multiworld.get_entrance("Matataki -> WOF2", self.player),
                 lambda state: self.char_rules.goro_available_only(state, self.player))
        set_rule(self.multiworld.get_entrance("Matataki -> Queens", self.player),
                 lambda state: self.char_rules.goro_available_only(state, self.player))
        set_rule(self.multiworld.get_entrance("Queens -> SW1", self.player),
                 lambda state: True)
        set_rule(self.multiworld.get_entrance("Queens -> SW2", self.player),
                 lambda state: self.char_rules.ruby_available_only(state, self.player))
        set_rule(self.multiworld.get_entrance("Queens -> Muska", self.player),
                 lambda state: self.char_rules.ruby_available_only(state, self.player))
        set_rule(self.multiworld.get_entrance("Muska -> SMT1", self.player),
                 lambda state: True)
        set_rule(self.multiworld.get_entrance("Muska -> SMT2", self.player),
                 lambda state: self.char_rules.ungaga_available_only(state, self.player))
        set_rule(self.multiworld.get_entrance("Muska -> Factory", self.player),
                 lambda state: self.char_rules.ungaga_available_only(state, self.player))
        set_rule(self.multiworld.get_entrance("Factory -> MS1", self.player),
                 lambda state: True)
        set_rule(self.multiworld.get_entrance("Factory -> MS2", self.player),
                 lambda state: self.char_rules.osmond_available_only(state, self.player))
        # TODO double check this for different char_rules
        set_rule(self.multiworld.get_entrance("Factory -> DHC", self.player),
                 lambda state: self.char_rules.got_accessible(state, self.player))
        set_rule(self.multiworld.get_entrance("DHC -> GOT", self.player),
                 lambda state: True)

        # Set up completion goal
        match self.options.boss_goal:
            case 2:
                if self.options.all_bosses:
                    self.multiworld.completion_condition[self.player] =\
                        lambda state: self.boss_rules.two_bosses(state, self.player)
                else:
                    self.multiworld.completion_condition[self.player] =\
                        lambda state: self.boss_rules.utan_access(state, self.player) and \
                                      self.char_rules.goro_available(state, self.player)
            case 3:
                if self.options.all_bosses:
                    self.multiworld.completion_condition[self.player] =\
                        lambda state: self.boss_rules.three_bosses(state, self.player)
                else:
                    self.multiworld.completion_condition[self.player] =\
                        lambda state: self.boss_rules.saia_access(state, self.player) and\
                                      self.char_rules.ruby_available(state, self.player)
            case 4:
                if self.options.all_bosses:
                    self.multiworld.completion_condition[self.player] =\
                        lambda state: self.boss_rules.four_bosses(state, self.player)
                else:
                    self.multiworld.completion_condition[self.player] =\
                        lambda state: self.boss_rules.curse_access(state, self.player) and\
                                      self.char_rules.ungaga_available(state, self.player)
            case 5:
                if self.options.all_bosses:
                    self.multiworld.completion_condition[self.player] =\
                        lambda state: self.boss_rules.five_bosses(state, self.player)
                else:
                    self.multiworld.completion_condition[self.player] =\
                        lambda state: self.boss_rules.joe_access(state, self.player) and\
                                      self.char_rules.osmond_available(state, self.player)
            case 6:
                if self.options.all_bosses:
                    self.multiworld.completion_condition[self.player] =\
                        lambda state: self.boss_rules.six_bosses(state, self.player, self.options.genie_pieces.value)
                else:
                    self.multiworld.completion_condition[self.player] =\
                        lambda state: self.boss_rules.genie_access(state, self.player, self.options.genie_pieces.value) and\
                                      self.char_rules.osmond_available(state, self.player)

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
                "genie_pieces": self.options.genie_pieces.value,
                "open_dungeon": self.options.open_dungeon.value,
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