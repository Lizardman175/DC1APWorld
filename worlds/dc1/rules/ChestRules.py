from BaseClasses import CollectionState

def xiao_available_only(state: CollectionState, player: int) -> bool:
    return state.has_all(["Stray Cat", "Gaffer's Lamp", "Pike"], player)

def xiao_available_only_ut(state: CollectionState, player: int) -> bool:
    return state.has("Stray Cat", player)

def goro_available_only(state: CollectionState, player: int) -> bool:
    return state.has_all(["Matataki River H", "Cacao's Laundry"], player)

def goro_available_only_ut(state: CollectionState, player: int) -> bool:
    return state.has_all(["Matataki River E", "Cacao's Laundry"], player)

def ruby_available_only(state: CollectionState, player: int) -> bool:
    return state.has("King's Lamp", player)

def ungaga_available_only(state: CollectionState, player: int) -> bool:
    return state.has("Sisters' Odds & Ends", player)