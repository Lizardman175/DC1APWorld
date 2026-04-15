from BaseClasses import CollectionState
from worlds.dc1.rules.CharRulesInterface import CharRulesInterface


class CharRules(CharRulesInterface):
    def xiao_available(self, state: CollectionState, player: int) -> bool:
        return state.has_all(["Stray Cat", "Gaffer's Lamp", "Pike"], player)

    def goro_available_only(self, state: CollectionState, player: int) -> bool:
        return state.has_all(["Matataki River H", "Cacao's Laundry"], player)

    def goro_available(self, state: CollectionState, player: int) -> bool:
        return self.goro_available_only(state, player) and self.xiao_available(state, player)

    def ruby_available_only(self, state: CollectionState, player: int) -> bool:
        return state.has("King's Lamp", player)

    def ruby_available(self, state: CollectionState, player: int) -> bool:
        return self.ruby_available_only(state, player) and self.goro_available(state, player)

    def ungaga_available_only(self, state: CollectionState, player: int) -> bool:
        return state.has("Sisters' Odds & Ends", player)

    def ungaga_available(self, state: CollectionState, player: int) -> bool:
        return self.ungaga_available_only(state, player) and self.ruby_available(state, player)

    def osmond_available_only(self, state: CollectionState, player: int) -> bool:
        return self.ungaga_available_only(state, player)

    def osmond_available(self, state: CollectionState, player: int) -> bool:
        return self.ungaga_available(state, player)

    def got_accessible(self, state: CollectionState, player: int) -> bool:
        return self.osmond_available(state, player)