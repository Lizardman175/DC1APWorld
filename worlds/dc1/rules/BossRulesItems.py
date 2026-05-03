from BaseClasses import CollectionState
from worlds.dc1 import BossRules


class BossRulesItems(BossRules):
    """Boss rule logic variants for chest shuffle on."""

    def dran_access(self, state: CollectionState, player: int) -> bool:
        return state.has("Horned Key", player)

    def utan_access(self, state: CollectionState, player: int) -> bool:
        return state.has_all(["Mushroom Balcony", "Sundew"], player)
