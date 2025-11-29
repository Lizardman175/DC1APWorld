from BaseClasses import CollectionState
from worlds.dc1.Options import DarkCloudOptions


def xiao_available(state: CollectionState, player: int) -> bool:
    return state.has("Stray Cat", player) and state.has("Gaffer's Lamp", player) and state.has("Pike", player)

def dran_accessible(state: CollectionState, player: int, options: DarkCloudOptions) -> bool:
    r = state.has("Dran's Sign", player) and \
        xiao_available(state, player)

    if r and options.miracle_sanity:
        r = state.has("Fluffy Doughnut", player, 1) and state.has("Fish Candy", player, 1) and \
            state.has("Fruit of Eden", player, 2)

    return r

def goro_available(state: CollectionState, player: int) -> bool:
    return state.has("Matataki River H", player) and state.has("Cacao's Laundry", player) and \
        xiao_available(state, player)

def utan_accessible(state: CollectionState, player: int, options: DarkCloudOptions) -> bool:
    r = state.has("Mushroom Balcony", player) and goro_available(state, player)

    if r and options.miracle_sanity:
        r = state.has("Fluffy Doughnut", player, 2) and state.has("Fish Candy", player, 2) and\
            state.has("Grass Cake", player, 1) and state.has("Fruit of Eden", player, 5)
        if r and options.sundew_chest:
            r = state.has("Sundew", player)

    return r

def ruby_available( state: CollectionState, player: int) -> bool:
    return state.has("King's Lamp", player) and goro_available(state, player)

def saia_accessible( state: CollectionState, player: int, options: DarkCloudOptions) -> bool:
    r = state.has("Cathedral's Holy Mark", player) and state.has("Divining House Sign", player) and \
        ruby_available(state, player)

    if r and options.miracle_sanity:
        r = state.has("Fluffy Doughnut", player, 3) and state.has("Fish Candy", player, 3) and \
            state.has("Grass Cake", player, 2) and state.has("Witch Parfait", player, 1) and \
            state.has("Fruit of Eden", player, 8)

    return r

def ungaga_available(state: CollectionState, player: int) -> bool:
    return state.has("Sisters' Odds & Ends", player) and ruby_available(state, player)

def curse_accessible(state: CollectionState, player: int, options: DarkCloudOptions) -> bool:
    r = state.has("Chief Bonka's Cabin 2", player) and state.has("Zabo's Hay", player) and \
        state.has("Enga's Roof", player) and ungaga_available(state, player)

    if r and options.miracle_sanity:
        r = state.has("Fluffy Doughnut", player, 4) and state.has("Fish Candy", player, 4) and\
            state.has("Grass Cake", player, 3) and state.has("Witch Parfait", player, 2) and \
            state.has("Scorpion Jerky", player, 1) and state.has("Fruit of Eden", player, 11)

    return r

def osmond_available(state: CollectionState, player: int) -> bool:
    return ungaga_available(state, player)

def joe_accessible(state: CollectionState, player: int, options: DarkCloudOptions) -> bool:
    # Just need to finish the head for the admission ticket.
    r = state.has("Eye (HD)", player) and ungaga_available(state, player)

    if r and options.miracle_sanity:
        r = state.has("Fluffy Doughnut", player, 4) and state.has("Fish Candy", player, 4) and\
            state.has("Grass Cake", player, 3) and state.has("Witch Parfait", player, 2) and \
            state.has("Scorpion Jerky", player, 1) and state.has("Carrot Cookie", player, 1) and \
            state.has("Fruit of Eden", player, 14)

    return r

def got_accessible(state: CollectionState, player: int) -> bool:
    return osmond_available(state, player)

def genie_accessible(state: CollectionState, player: int, options: DarkCloudOptions) -> bool:
    r = state.has("Book of Curses (Departure)", player) \
        and state.has("The Broken Sword (Things Lost)", player) \
        and state.has("Black Blood (Demon)", player) and state.has("Bloody Dress (Protected)", player) \
        and state.has("Assassin (Assassin)", player) and state.has("Sophia (Dark Power)", player) \
        and state.has("Bloody Agreement (The Deal)", player) and state.has("Sophia (Menace)", player) \
        and state.has("Crown (Campaign)", player) and state.has("Buggy (Reunion)", player) \
        and state.has("Sophia (Ceremony)", player) and state.has("Crown (Crowning Day)", player) \
        and osmond_available(state, player)

    if r and options.miracle_sanity:
        r = state.has("Fluffy Doughnut", player, 5) and state.has("Fish Candy", player, 5) and \
            state.has("Grass Cake", player, 4) and state.has("Witch Parfait", player, 3) and \
            state.has("Scorpion Jerky", player, 2) and state.has("Carrot Cookie", player, 1) and \
            state.has("Fruit of Eden", player, 18)

    return r

def chest_test(state: CollectionState, player: int, character: str = None, geo: list[str] = None) -> bool:
    r = True

    if geo:
        for g in geo:
            r = state.has(g, player)
            if not r:
                break

    if r and character:
        if character == "xiao":
            r = xiao_available(state, player)
        elif character == "goro":
            r = goro_available(state, player)
        elif character == "ruby":
            r = ruby_available(state, player)
        elif character == "ungaga":
            r = ungaga_available(state, player)
        elif character == "osmond":
            r = osmond_available(state, player)

    return r
