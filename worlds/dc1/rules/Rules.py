from rule_builder.options import OptionFilter
from rule_builder.rules import HasAll, Has, HasAllCounts, And, HasAny, HasFromListUnique, CanReachRegion, Rule, False_, \
    True_
from worlds.dc1.Options import AllBosses, MiracleSanity, DarkCloudOptions

chest_shuffle_off = OptionFilter(MiracleSanity, False)
all_bosses_off = OptionFilter(AllBosses, False)

r_goro_items = HasAllCounts({"Fluffy Doughnut": 1, "Fish Candy": 1, "Fruit of Eden": 2, "Pocket": 1})
r_ruby_items = HasAllCounts({"Fluffy Doughnut": 2, "Fish Candy": 2, "Grass Cake": 1, "Fruit of Eden": 6, "Pocket": 2})
r_ungaga_items = HasAllCounts({"Fluffy Doughnut": 3, "Fish Candy": 3, "Grass Cake": 2,
                               "Witch Parfait": 1, "Fruit of Eden": 10, "Pocket": 3})
r_osmond_items = HasAllCounts({"Fluffy Doughnut": 4, "Fish Candy": 4, "Grass Cake": 3,
                               "Witch Parfait": 2, "Scorpion Jerky": 1, "Fruit of Eden": 14, "Pocket": 3})

r_gaffer = HasAll("Gaffer's Lamp", "Pike")
r_owl = Has("Wise Owl Entrance")
r_ruty = Has("Ruty's Pushcart 3")
r_suzy = Has("Suzy's Lamp")
r_lana = Has("Lana's Pushcart 1")
r_joker = HasAll("Joker's Lamp", "Sheriff's Sign")
r_brooke = Has("Brooke's Hay")
r_ledan = True_()
r_simba = True_()

r_xiao_available_only_ut = Has("Stray Cat")
r_xiao_available_only = And(r_gaffer, r_xiao_available_only_ut)
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

# Ruby required for the better shop completion cutscene reward first
r_jack = And(Has("Jack's Lamp"), r_ruby_available_only)

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

    r_two_bosses = And(r_dran_access, r_utan_access)
    r_three_bosses = And(r_two_bosses, r_saia_access)
    r_four_bosses = And(r_three_bosses, r_curse_access)
    r_five_bosses = And(r_four_bosses, r_joe_access)
    r_six_bosses = And(r_five_bosses, r_genie_access)

    r_goal = False_()

    match options.boss_goal:
        case 2:
            if all_bosses_off:
                r_goal = And(CanReachRegion("WOF2"), r_utan_access)
            else:
                r_goal = And(CanReachRegion("WOF2"), r_two_bosses)
        case 3:
            if all_bosses_off:
                r_goal = And(CanReachRegion("SW2"), r_saia_access)
            else:
                r_goal = And(CanReachRegion("SW2"), r_three_bosses)
        case 4:
            if all_bosses_off:
                r_goal = And(CanReachRegion("SMT2"), r_curse_access)
            else:
                r_goal = And(CanReachRegion("SMT2"), r_four_bosses)
        case 5:
            if all_bosses_off:
                r_goal = And(CanReachRegion("MS2"), r_joe_access)
            else:
                r_goal = And(CanReachRegion("MS2"), r_five_bosses)
        case 6:
            if all_bosses_off:
                r_goal = And(CanReachRegion("GOT"), r_genie_access)
            else:
                r_goal = And(CanReachRegion("GOT"), r_six_bosses)

    return r_goal