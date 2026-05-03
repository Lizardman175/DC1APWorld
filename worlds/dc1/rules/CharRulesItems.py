from BaseClasses import CollectionState
from worlds.dc1.rules.CharRules import CharRules


def goro_items(state: CollectionState, player: int) -> bool:
    return state.has_all_counts({"Fluffy Doughnut": 1, "Fish Candy": 1, "Fruit of Eden": 2,
                                  "Pocket": 1}, player)

def ruby_items(state: CollectionState, player: int) -> bool:
    return state.has_all_counts({"Fluffy Doughnut": 2, "Fish Candy": 2, "Grass Cake": 1,
                                  "Fruit of Eden": 6, "Pocket": 2}, player)

def ungaga_items(state: CollectionState, player: int) -> bool:
    return state.has_all_counts({"Fluffy Doughnut": 3, "Fish Candy": 3, "Grass Cake": 2,
                          "Witch Parfait": 1, "Fruit of Eden": 10, "Pocket": 3}, player)

def osmond_items(state: CollectionState, player: int) -> bool:
    return state.has_all_counts({"Fluffy Doughnut": 4, "Fish Candy": 4, "Grass Cake": 3,
                          "Witch Parfait": 2, "Scorpion Jerky": 1, "Fruit of Eden": 14,
                          "Pocket": 3}, player)


class CharRulesItems(CharRules):
    # Currently the same as parent class
    #def xiao_available(self, state: CollectionState, player: int) -> bool:
        #return state.has_all(["Stray Cat", "Gaffer's Lamp", "Pike"], player)

    def goro_available_only(self, state: CollectionState, player: int) -> bool:
        return super().goro_available_only(state, player) and goro_items(state, player)

    def goro_available(self, state: CollectionState, player: int) -> bool:
        return super().goro_available(state, player) and goro_items(state, player)

    def ruby_available_only(self, state: CollectionState, player: int) -> bool:
        return super().ruby_available_only(state, player) and ruby_items(state, player)

    def ruby_available(self, state: CollectionState, player: int) -> bool:
        return super().ruby_available(state, player) and ruby_items(state, player)

    def ungaga_available_only(self, state: CollectionState, player: int) -> bool:
        return super().ungaga_available_only(state, player) and ungaga_items(state, player)

    def ungaga_available(self, state: CollectionState, player: int) -> bool:
        return super().ungaga_available(state, player) and ungaga_items(state, player)

    def osmond_available_only(self, state: CollectionState, player: int) -> bool:
        return super().osmond_available_only(state, player) and osmond_items(state, player)

    def osmond_available(self, state: CollectionState, player: int) -> bool:
        return super().osmond_available(state, player) and osmond_items(state, player)

    # def got_accessible(self, state: CollectionState, player: int) -> bool:
    #     return super().got_accessible(state, player)