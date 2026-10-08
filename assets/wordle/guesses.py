# Secret words that the game can select as the answer
TARGET_WORDS = [
    "ABODE", "ACORN", "ACUTE", "AGILE", "AMBER", "ANGEL", "APPLE", "BEACH",
    "BLAST", "BLINK", "BRAVE", "BREAD", "BRICK", "CABIN", "CANDY", "CHALK",
    "CHARM", "CHESS", "CLEAN", "CRANE", "CRISP", "CROWN", "DANCE", "DREAM",
    "DRIVE", "EAGLE", "EARTH", "FLAME", "FLASH", "FLUTE", "FOCUS", "FROST",
    "GLINT", "GLOBE", "GRACE", "GRAPE", "GREEN", "HEART", "HOUSE", "IMAGE",
    "JUICE", "KNIFE", "LEMON", "LIGHT", "LUNAR", "MANGO", "MAPLE", "MUSIC",
    "OCEAN", "OCTAL", "PIANO", "PLANT", "PRISM", "PULSE", "QUART", "QUEST",
    "QUICK", "QUIET", "RADAR", "RELAX", "ROBOT", "SHARK", "SHINE", "SKATE",
    "SMILE", "SNAKE", "SOLAR", "SPARK", "STORM", "SUGAR", "SWEET", "TIGER",
    "TRAIN", "TREND", "VALLEY", "VORTEX", "WATER", "WHITE", "WORLD", "YOUTH"
]

# Additional valid guesses allowed during gameplay
VALID_GUESSES = [
    "AAHED", "AALII", "AARGH", "ABACA", "ABACI", "ABACK", "ABAFT", "ABAMP",
    "ABAND", "ABASE", "ABASH", "ABATE", "ABBAS", "ABBED", "ABBEY", "ABBOT",
    "ABCEE", "ABEAR", "ABETS", "ABHOR", "ABIDE", "ABIES", "ABLED", "ABLER",
    "ABLES", "ABLET", "ABLOW", "ABMHO", "ABODE", "ABOHM", "ABOIL", "ABOMA",
    "ABOON", "ABORD", "ABORE", "ABORT", "ABOUT", "ABOVE", "ABRAY", "ABRIM",
    "ABRIN", "ABRIS", "ABSEY", "ABSIT", "ABUNA", "ABUNE", "ABUSE", "ABUTS",
    "ABUZZ", "ABYES", "ABYSM", "ABYSS", "ACARI", "ACCAS", "ACCOY", "ACERB",
    "ACERS", "ACETA", "ACHED", "ACHES", "ACHOO", "ACIDS", "ACIDY", "ACING",
    "ACINI", "ACKEE", "ACKER", "ACMES", "ACMIC", "ACNED", "ACNES", "ACOCK"
]

# The complete dictionary allowed for player input
FULL_DICTIONARY = set(TARGET_WORDS + VALID_GUESSES)