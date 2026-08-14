from rule_builder.rules import Has, And, CanReachRegion, Or
from worlds.dc1.JunkDrawer import glitch_name
from worlds.dc1.rules.Rules import r_owl, r_ruty, r_lana, r_brooke

r_bait_shops = Or(And(CanReachRegion("Matataki"), r_owl),
                  And(CanReachRegion("Queens"), Or(r_ruty, r_lana)))

r_norune_pond = Has("Norune Pond")
r_peanut_pond = Has("Matataki River E")
r_rod = Has("Fishing Rod")

# Queens fishing spot
r_ocean_fish = And(r_rod, r_ruty)
# Oasis
r_desert_fish = And(r_rod, Has("Oasis"), Or(r_bait_shops, r_brooke))
r_niler_fish = And(r_rod, r_norune_pond, r_bait_shops)
# Also used for Nonky
r_gummy_fish = And(r_rod, Or(r_norune_pond, CanReachRegion("Matataki")), r_bait_shops)
r_gobbler_fish = And(r_rod,
                     Or(r_norune_pond, And(r_peanut_pond, CanReachRegion("Matataki"))),
                     r_bait_shops)
r_baku_fish = And(r_rod, r_bait_shops)
r_tarton_fish = And(r_rod, r_peanut_pond, r_bait_shops)
# Client adds carrots to owl shop
r_umadakara_fish = And(r_rod, CanReachRegion("Matataki"), r_peanut_pond, r_owl)
# Muska/Brooke for bait shop, otherwise fish is available in Matataki
r_baron_fish = And(r_rod, CanReachRegion("Muska"), r_brooke)
# Queens/Lana for bait shop, otherwise fish is available in Matataki
r_mardan_fish = And(r_rod, CanReachRegion("Queens"), r_lana)

# "Glitched" fish logic for UT to show without shops
r_ocean_fish_ut = And(r_rod, Or(r_ruty, Has(glitch_name)))
# Oasis
r_desert_fish_ut = And(r_rod, Has("Oasis"), Or(r_bait_shops, r_brooke, Has(glitch_name)))
r_niler_fish_ut = And(r_rod, r_norune_pond, Or(r_bait_shops, Has(glitch_name)))
# Also used for Nonky
r_gummy_fish_ut = And(r_rod, Or(r_norune_pond, CanReachRegion("Matataki")), Or(r_bait_shops, Has(glitch_name)))
r_gobbler_fish_ut = And(r_rod,
                        Or(r_norune_pond, And(r_peanut_pond, CanReachRegion("Matataki"))),
                        Or(r_bait_shops, Has(glitch_name)))
r_baku_fish_ut = And(r_rod, Or(r_bait_shops, Has(glitch_name)))
r_tarton_fish_ut = And(r_rod, r_peanut_pond, Or(r_bait_shops, Has(glitch_name)))
# Client adds carrots to owl shop
r_umadakara_fish_ut = And(r_rod, CanReachRegion("Matataki"), r_peanut_pond, Or(r_owl, Has(glitch_name)))
# Muska/Brooke for bait shop, otherwise fish is available in Matataki
r_baron_fish_ut = And(r_rod, CanReachRegion("Matataki"), Or(r_brooke, Has(glitch_name)))
# Queens/Lana for bait shop, otherwise fish is available in Matataki
r_mardan_fish_ut = And(r_rod, CanReachRegion("Matataki"), Or(r_lana, Has(glitch_name)))