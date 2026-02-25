from BaseClasses import CollectionState
from worlds.dc1.rules.CharRules import CharRules

# A more minimal set of rules for Xiao/Goro for tracker purposes
class CharRulesUT(CharRules):
    def xiao_available(self, state: CollectionState, player: int) -> bool:
        return state.has("Stray Cat", player)

    def goro_available(self, state: CollectionState, player: int) -> bool:
        return state.has_all(["Matataki River E", "Cacao's Laundry"], player) and \
            self.xiao_available(state, player)

    # def ruby_available(self, state: CollectionState, player: int) -> bool:
    #
    # def ungaga_available(self, state: CollectionState, player: int) -> bool:
    #
    # def osmond_available(self, state: CollectionState, player: int) -> bool:
    #
    # def got_accessible(self, state: CollectionState, player: int) -> bool:
