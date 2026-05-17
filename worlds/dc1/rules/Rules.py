from rule_builder.options import OptionFilter
from rule_builder.rules import HasAll, Has, HasAllCounts, And, HasAny, HasFromListUnique, CanReachRegion, Rule, False_
from worlds.dc1.Options import AllBosses, MiracleSanity, DarkCloudOptions

chest_shuffle_off = OptionFilter(MiracleSanity, False)
all_bosses_off = OptionFilter(AllBosses, False)

r_goro_items = HasAllCounts({"Fluffy Doughnut": 1, "Fish Candy": 1, "Fruit of Eden": 2, "Pocket": 1})
r_ruby_items = HasAllCounts({"Fluffy Doughnut": 2, "Fish Candy": 2, "Grass Cake": 1, "Fruit of Eden": 6, "Pocket": 2})
r_ungaga_items = HasAllCounts({"Fluffy Doughnut": 3, "Fish Candy": 3, "Grass Cake": 2,
                               "Witch Parfait": 1, "Fruit of Eden": 10, "Pocket": 3})
r_osmond_items = HasAllCounts({"Fluffy Doughnut": 4, "Fish Candy": 4, "Grass Cake": 3,
                               "Witch Parfait": 2, "Scorpion Jerky": 1, "Fruit of Eden": 14, "Pocket": 3})

r_xiao_available_only = HasAll("Stray Cat", "Gaffer's Lamp", "Pike")
r_xiao_available_only_ut = Has("Stray Cat")
r_goro_available_only = HasAll("Matataki River H", "Cacao's Laundry")
r_goro_available_only_ut = HasAll("Matataki River E", "Cacao's Laundry")
r_ruby_available_only = Has("King's Lamp")
r_ungaga_available_only = Has("Sisters' Odds & Ends")
r_osmond_available_only = r_ungaga_available_only

r_goro_available = r_goro_available_only & (chest_shuffle_off | r_goro_items)
r_ruby_available = r_ruby_available_only & (chest_shuffle_off | r_ruby_items)
r_ungaga_available = r_ungaga_available_only & (chest_shuffle_off | r_ungaga_items)
r_osmond_available = r_osmond_available_only & (chest_shuffle_off | r_osmond_items)
r_dhc_available = And(HasAny("Tomahon", "Boon"), HasAny("Gotch", "Amuleo"))

def get_completion_rule(options: DarkCloudOptions) -> Rule:

    r_dran_access = (OptionFilter(MiracleSanity, False) & Has("Dran's Sign")) | Has("Horned Key")
    r_utan_access = Has("Mushroom Balcony") & (OptionFilter(MiracleSanity, False) | Has("Sundew"))
    r_saia_access = HasAll("Cathedral's Holy Mark", "Divining House Sign")
    r_curse_access = HasAll("Chief Bonka's Cabin 2", "Zabo's Hay", "Enga's Roof")
    r_joe_access = Has("Eye (HD)")

    r_genie_access = HasFromListUnique("Book of Curses (Departure)", "The Broken Sword (Things Lost)",
                                    "Black Blood (Demon)", "Bloody Dress (Protected)", "Assassin (Assassin)", "Sophia (Dark Power)",
                                  "Bloody Agreement (The Deal)", "Sophia (Menace)", "Crown (Campaign)",
                                  "Buggy (Reunion)", "Sophia (Ceremony)", "Crown (Crowning Day)", count=options.memory_count.value)

    r_two_bosses = r_dran_access & r_utan_access
    r_three_bosses = r_two_bosses & r_saia_access
    r_four_bosses = r_three_bosses & r_curse_access
    r_five_bosses = r_four_bosses & r_joe_access
    r_six_bosses = r_five_bosses & r_genie_access

    r_goal = False_()

    match options.boss_goal:
        case 2:
            r_goal = CanReachRegion("WOF2") & ((all_bosses_off & r_utan_access) | r_two_bosses)
        case 3:
            r_goal = CanReachRegion("SW2") & ((all_bosses_off & r_saia_access) | r_three_bosses)
        case 4:
            r_goal = CanReachRegion("SMT2") & ((all_bosses_off & r_curse_access) | r_four_bosses)
        case 5:
            r_goal = CanReachRegion("MS2") & ((all_bosses_off & r_joe_access) | r_five_bosses)
        case 6:
            r_goal = CanReachRegion("GOT") & ((all_bosses_off & r_genie_access) | r_six_bosses)

    return r_goal