from enum import Enum

class PlantType(str, Enum):
    veggie = "veggie"
    herb = "herb"
    fruit = "fruit"
    flower = "flower"

class SunlightLevel(str, Enum):
    full = "full"
    partial = "partial"
    shade = "shade"

class WaterLevel(str, Enum):
    high="high"
    medium="medium"
    low="low"

class TierType(str, Enum):
    original = "original" # deeper pockets can support longer roots
    leaf = "leaf" # shallower pockets can support more compact, shallow root plants

class TierSupport(str, Enum):
    original_only = "original_only" # plant has deeper roots so leaf is not suitable
    both = "both" # plant can fit in either leaf or original

class GreenStalkColor(str, Enum):
    # current and most common colors from their catalog
    beautiful_black = "beautiful_black"
    blackberry = "blackberry"
    blueberry = "blueberry"
    cherry_blossom = "cherry_blossom"
    chocolate_brown = "chocolate_brown"
    evergreen = "evergreen"
    glacier_blue = "glacier_blue"
    lemon = "lemon"
    lilac = "lilac"
    luscious_green = "luscious_green"
    maple= "maple"
    oasis = "oasis"
    pepper_corn = "pepper_corn"
    razzleberry = "razzleberry"
    rusted_garden_red = "rusted_garden_red"
    sage = "sage"
    stone = "stone"
    terracotta = "terracotta"
    tomato = "tomato"