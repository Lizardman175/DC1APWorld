import re
from dataclasses import dataclass
from Options import Choice, Toggle, PerGameCommonOptions, Range, DeathLink, FreeText, OptionError


class Goal(Range):
    """Select Dungeon from 2-6 to be the goal."""
    display_name = "Boss Goal"
    default = 6
    range_start = 2
    range_end = 6

class AllBosses(Toggle):
    """Requires defeating every boss up to the goal boss in order to finish the game."""
    display_name = "All Bosses"
    default = 0

class RequiredMemoryCount(Range):
    """How many complete pieces of Seda's memory are required for access to the Dark Genie. No effect if boss goal is less than 6."""
    display_name = "Required Memory Count"
    default = 12
    range_start = 4
    range_end = 12

class OpenDungeon(Choice):
    """Open all dungeon floors as they become logically available."""
    display_name = "Open Dungeon"
    default = 1
    option_closed = 0
    option_open = 1

class ProgressiveCharRecruitment(Toggle):
    """Makes all character recruitment buildings one progressive item.  Useful for long/large multiworlds.
    All Player House pieces will be received, followed by Cacao's House starting at item 8, etc."""
    display_name = "Progressive Char Recruitment"
    default = 1

class ExtraCharBuildingPieces(Toggle):
    """Adds an extra of each character recruitment building to the item pool as well as an extra Matataki River
    in place of a number of Well parts. What building parts are reflected by the progressive_chars option.
    Adds a little extra progression speed to larger multiworlds."""
    display_name = "Extra Char Building Pieces"
    default = 0

class BetterStartingWeapons(Toggle):
    """Give each character a Tier 1 weapon in addition to their unbreakable starter."""
    display_name = "Better Starting Weapons"
    default = 1

class MiracleSanity(Toggle):
    """Add miracle chests to the item pool."""
    display_name = "Chest Sanity"
    default = 0

class ShopSanity(Toggle):
    """Add 2 items to each shop (excluding Rando).  Gaffer will have 2 items temporarily replaced if the full shop is
    unlocked."""
    display_name = "Shop Sanity"
    default = 0

class FishSanity(Choice):
    """Catching each fish once is a location.  Adds carrots to Wise Owl Shop inventory for Umadakara.
    all_fish includes the Garayan fish as well.  Mardan Garayans require Queens (boss goal 3+) to
    purchase poisonous apples and Baron Garayan Muska Lacka (boss goal 4+) for potato cakes."""
    display_name = "Fish Sanity"
    option_none = 0
    option_most_fish = 1
    option_all_fish = 2
    default = 0

class AbsMultiplier(Choice):
    """Adjust the ABS gained from enemies."""
    display_name = "ABS Multiplier"
    option_half = 0
    option_normal = 1
    option_one_and_half = 2
    option_double = 3
    option_double_and_half = 4
    option_triple = 5
    default = 3

class AttachmentMultiplierConfig(Choice):
    """Enable attachment multiplier for all attachments, only those from MW, or no attachments."""
    display_name = "Attachment Multiplier Config"
    option_none = 1
    option_mw_only = 2
    option_all = 3
    default = 3

class AttachmentMultiplierValue(Choice):
    """Adjust the value of attachments. Does not affect attack/speed/magic/endurance received normally in game."""
    display_name = "Attachment Multiplier"
    option_normal = 1
    option_one_and_half = 2
    option_double = 3
    default = 2

class AutoBuild(Choice):
    """Automatically places building pieces as received.
    Hundo places buildings for 100% town completion.
    Any percent places only buildings with chests clustered similar to how speed runs place them.
    Muska only auto builds only Muska Lacka for 100%, robot only the sun giant and muska/robot builds both."""
    display_name = "Auto Build Buildings"
    option_off = 0
    option_any_percent = 1
    option_hundo = 2
    option_muska_only = 3
    option_robot_only = 4
    option_muska_robot_only = 5
    default = 2

class ToanName(FreeText):
    """Default name for Toan.
    1-10 characters.  Valid Characters: A-Z, a-z, 0-9, '="!?#&+-*/%~()@|<>[]{}:,.$, space
    Anything outside that range will fail generation.

    NOTE: Must connect before hitting Start Game for Toan's name to be affected."""
    display_name = "Toan's Default Name"
    default = "Toan"

    def __init__(self, value:str):
        super(ToanName, self).__init__(value.strip())
        test_char_name("Toan", self.value)

class XiaoName(FreeText):
    """Default name for Xiao.
    1-10 characters.  Valid Characters: A-Z, a-z, 0-9, '="!?#&+-*/%~()@|<>[]{}:,.$, space
    Cannot start with a space. Anything outside that range will fail generation."""
    display_name = "Xiao's Default Name"
    default = "Xiao"

    def __init__(self, value:str):
        super(XiaoName, self).__init__(value.strip())
        test_char_name("Xiao", self.value)

class GoroName(FreeText):
    """Default name for Goro.
    1-10 characters.  Valid Characters: A-Z, a-z, 0-9, '="!?#&+-*/%~()@|<>[]{}:,.$, space
    Cannot start with a space. Anything outside that range will fail generation."""
    display_name = "Goro's Default Name"
    default = "Goro"

    def __init__(self, value:str):
        super(GoroName, self).__init__(value.strip())
        test_char_name("Goro", self.value)

class RubyName(FreeText):
    """Default name for Ruby.
    1-10 characters.  Valid Characters: A-Z, a-z, 0-9, '="!?#&+-*/%~()@|<>[]{}:,.$, space
    Cannot start with a space. Anything outside that range will fail generation."""
    display_name = "Ruby's Default Name"
    default = "Ruby"

    def __init__(self, value:str):
        super(RubyName, self).__init__(value.strip())
        test_char_name("Ruby", self.value)

class UngagaName(FreeText):
    """Default name for Ungaga.
    1-10 characters.  Valid Characters: A-Z, a-z, 0-9, '="!?#&+-*/%~()@|<>[]{}:,.$, space
    Cannot start with a space. Anything outside that range will fail generation."""
    display_name = "Ungaga's Default Name"
    default = "Ungaga"

    def __init__(self, value:str):
        super(UngagaName, self).__init__(value.strip())
        test_char_name("Ungaga", self.value)

class OsmondName(FreeText):
    """Default name for Osmond.
    1-10 characters.  Valid Characters: A-Z, a-z, 0-9, '="!?#&+-*/%~()@|<>[]{}:,.$, space
    Cannot start with a space. Anything outside that range will fail generation."""
    display_name = "Osmond's Default Name"
    default = "Osmond"

    def __init__(self, value:str):
        super(OsmondName, self).__init__(value.strip())
        test_char_name("Osmond", self.value)

@dataclass
class DarkCloudOptions(PerGameCommonOptions):
    boss_goal: Goal
    all_bosses: AllBosses
    memory_count: RequiredMemoryCount
    open_dungeon: OpenDungeon
    progressive_chars: ProgressiveCharRecruitment
    extra_char_buildings: ExtraCharBuildingPieces
    starter_weapons: BetterStartingWeapons
    miracle_sanity: MiracleSanity
    shop_sanity: ShopSanity
    fish_sanity: FishSanity
    abs_multiplier: AbsMultiplier
    attach_multiplier: AttachmentMultiplierValue
    attach_mult_config: AttachmentMultiplierConfig
    auto_build: AutoBuild
    death_link: DeathLink
    toan_name: ToanName
    xiao_name: XiaoName
    goro_name: GoroName
    ruby_name: RubyName
    ungaga_name: UngagaName
    osmond_name: OsmondName

# Patterns for Name option validation
valid_pattern = r"[a-zA-Z0-9'=\"!?#&+\-*/%~()@|<>\[\]{}:,.$][a-zA-Z0-9'=\"!?#&+\-*/%~()@|<>\[\]{}:,.$ ]*"
len_pattern = r"[a-zA-Z0-9'=\"!?#&+\-*/%~()@|<>\[\]{}:,.$ ]{1,10}"

def test_char_name(char:str, name:str) -> None:
    if not re.fullmatch(valid_pattern, name):
        raise NameCharException(char, name)
    if not re.fullmatch(len_pattern, name):
        raise NameLenException(char, name)

class NameCharException(OptionError):
    def __init__(self, message:str, name:str):
        self.message = message + "'s name contains invalid characters: " + name
        super().__init__(self.message)

class NameLenException(OptionError):
    def __init__(self, message:str, name:str):
        self.message = message + "'s name is invalid: '" + name + "'. Must be from 1 to 10 characters."
        super().__init__(self.message)