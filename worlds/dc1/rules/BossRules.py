from BaseClasses import CollectionState
from worlds.dc1 import DarkCloudOptions
from worlds.dc1.rules.CharRulesInterface import CharRulesInterface


class BossRules:

    char_rules: CharRulesInterface = None

    def set_char_rules(self, char_rules: CharRulesInterface):
        self.char_rules = char_rules

    def dran_access(self, state: CollectionState, player: int) -> bool:
        return state.has("Dran's Sign", player)

    def utan_access(self, state: CollectionState, player: int) -> bool:
        return state.has("Mushroom Balcony", player)

    def saia_access(self, state: CollectionState, player: int) -> bool:
        return state.has_all(["Cathedral's Holy Mark", "Divining House Sign"], player)

    def curse_access(self, state: CollectionState, player: int) -> bool:
        return state.has_all(["Chief Bonka's Cabin 2", "Zabo's Hay", "Enga's Roof"], player)

    def joe_access(self, state: CollectionState, player: int) -> bool:
        # Just need to finish the head for the admission ticket.
        return state.has("Eye (HD)", player)

    def genie_access(self, state: CollectionState, player: int, count: int) -> bool:
        return state.has_from_list_unique(["Book of Curses (Departure)", "The Broken Sword (Things Lost)", "Black Blood (Demon)",
                              "Bloody Dress (Protected)", "Assassin (Assassin)", "Sophia (Dark Power)",
                              "Bloody Agreement (The Deal)", "Sophia (Menace)", "Crown (Campaign)",
                              "Buggy (Reunion)", "Sophia (Ceremony)", "Crown (Crowning Day)"], player, count)

    def two_bosses(self, state: CollectionState, player: int) -> bool:
        return self.utan_access(state, player) and self.dran_access(state, player) and self.char_rules.goro_available(state, player)

    def three_bosses(self, state: CollectionState, player: int) -> bool:
        return self.saia_access(state, player) and self.utan_access(state, player) and self.dran_access(state, player) and \
            self.char_rules.ruby_available(state, player)

    def four_bosses(self, state: CollectionState, player: int) -> bool:
        return self.curse_access(state, player) and self.saia_access(state, player) and self.utan_access(state, player) and \
            self.dran_access(state, player) and self.char_rules.ungaga_available(state, player)

    def five_bosses(self, state: CollectionState, player: int) -> bool:
        return self.joe_access(state, player) and self.curse_access(state, player) and self.saia_access(state, player) and \
            self.utan_access(state, player) and self.dran_access(state, player) and self.char_rules.osmond_available(state, player)

    def six_bosses(self, state: CollectionState, player: int, count: int) -> bool:
        return self.genie_access(state, player, count) and self.five_bosses(state, player)