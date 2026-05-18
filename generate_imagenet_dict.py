"""
Chạy script này 1 lần để sinh file imagenet_full.json (~1000 class)
> python generate_imagenet_dict.py
"""
import json, re
import torchvision.models as models

weights = models.ResNet50_Weights.IMAGENET1K_V1
CATS = weights.meta["categories"]   # list[str], 1000 entries

# ── Category rules (keyword → category + emoji + color) ─────────────────────
RULES = [
    (["dog","retriever","shepherd","poodle","terrier","husky","bulldog",
      "dalmatian","corgi","beagle","pug","chihuahua","dachshund","spaniel",
      "samoyed","malamute","collie","boxer","rottweiler","greyhound","whippet",
      "bloodhound","basset","doberman","schnauzer","chow","pekinese","shih",
      "papillon","borzoi","saluki","afghanhound","leonberg","newfoundland",
      "saint bernard","appenzeller","entlebucher","greater swiss"],
     "animal","🐶","#795548"),
    (["cat","kitten","tabby","persian","siamese","egyptian","angora"],
     "animal","🐱","#FF9800"),
    (["bird","robin","jay","finch","sparrow","crow","pigeon","dove","eagle",
      "hawk","owl","hummingbird","peacock","flamingo","toucan","parakeet",
      "macaw","cockatoo","parrot","ostrich","kite","vulture","albatross",
      "bulbul","junco","brambling","goldfinch","house finch","indigo bunting",
      "bee eater","hornbill","lorikeet"],
     "animal","🐦","#29B6F6"),
    (["fish","goldfish","shark","salmon","eel","ray","puffer","lionfish",
      "sturgeon","gar","stingray","tench"],
     "animal","🐟","#26C6DA"),
    (["snake","python","cobra","viper","boa","anaconda","kingsnake",
      "horned viper","thunder snake","ringneck"],
     "animal","🐍","#388E3C"),
    (["turtle","tortoise","terrapin"],  "animal","🐢","#66BB6A"),
    (["frog","toad","bullfrog","tree frog"], "animal","🐸","#4CAF50"),
    (["lizard","iguana","gecko","chameleon","agama","frilled"],
     "animal","🦎","#66BB6A"),
    (["spider","scorpion","tarantula"],  "animal","🕷️","#5D4037"),
    (["insect","beetle","butterfly","bee","ant","dragonfly","mantis","cricket",
      "cockroach","walking stick","lacewing","firefly","leafhopper"],
     "animal","🦋","#CE93D8"),
    (["elephant","mammoth"],            "animal","🐘","#90A4AE"),
    (["lion"],                          "animal","🦁","#FFB300"),
    (["tiger"],                         "animal","🐯","#FF8F00"),
    (["bear","panda","sloth bear"],     "animal","🐻","#6D4C41"),
    (["monkey","ape","chimpanzee","gorilla","baboon","gibbon","macaque",
      "colobus","proboscis","squirrel monkey","marmoset","spider monkey"],
     "animal","🐒","#A1887F"),
    (["penguin"],                       "animal","🐧","#455A64"),
    (["rabbit","hare"],                 "animal","🐰","#EF9A9A"),
    (["horse","pony","stallion","hartebeest","zebra"],
     "animal","🐴","#8D6E63"),
    (["cow","ox","bull","bison","water buffalo"],
     "animal","🐄","#BCAAA4"),
    (["pig","hog","boar","warthog"],    "animal","🐷","#F48FB1"),
    (["sheep","ram","goat","ibex"],     "animal","🐑","#ECEFF1"),
    (["deer","gazelle","impala","antelope","eland","kudu"],
     "animal","🦌","#A1887F"),
    (["camel","llama","alpaca"],        "animal","🐪","#FFD54F"),
    (["wolf","coyote","dhole","dingo"], "animal","🐺","#78909C"),
    (["fox"],                           "animal","🦊","#FF7043"),
    (["cat","leopard","cheetah","jaguar","cougar","lynx","snow leopard"],
     "animal","🐆","#FF8F00"),
    (["rhinoceros","hippopotamus"],     "animal","🦏","#90A4AE"),
    (["giraffe"],                       "animal","🦒","#FFB300"),
    (["kangaroo","wallaby"],            "animal","🦘","#A1887F"),
    (["hen","cock","rooster","chicken","prairie chicken","partridge",
      "quail","grouse"],               "animal","🐔","#FFF176"),
    (["duck","drake","mallard","goose","black swan"],
     "animal","🦆","#80DEEA"),
    (["shark","great white"],          "animal","🦈","#546E7A"),
    (["jellyfish","sea anemone","sea urchin","starfish","coral"],
     "animal","🪼","#CE93D8"),
    (["crab","lobster","crayfish","hermit crab"],
     "animal","🦀","#EF5350"),

    (["banana"],     "fruit","🍌","#FFD54F"),
    (["orange"],     "fruit","🍊","#FF7043"),
    (["lemon","lime"],"fruit","🍋","#FDD835"),
    (["strawberry"], "fruit","🍓","#E53935"),
    (["pineapple"],  "fruit","🍍","#FDD835"),
    (["fig"],        "fruit","🍑","#FF7043"),
    (["pomegranate"],"fruit","🍈","#E91E63"),
    (["grape"],      "fruit","🍇","#9B5DE5"),
    (["apple"],      "fruit","🍎","#FF5252"),
    (["cherry","acerola"],"fruit","🍒","#C62828"),
    (["mushroom","agaric","gyromitra","stinkhorn"],
     "nature","🍄","#A1887F"),

    (["pizza"],      "food","🍕","#FF7043"),
    (["hamburger","cheeseburger"],"food","🍔","#FF8F00"),
    (["hot dog","hotdog","corn dog"],"food","🌭","#F4511E"),
    (["ice cream","ice lolly","gelato"],"food","🍦","#F8BBD0"),
    (["cake","cupcake"],"food","🎂","#F48FB1"),
    (["bread","loaf","bagel","baguette"],"food","🍞","#FFCC80"),
    (["cookie","biscuit","pretzel"],"food","🍪","#FFAB40"),
    (["espresso","coffee","cappuccino"],"food","☕","#5D4037"),
    (["egg","eggnog"],"food","🥚","#FFF9C4"),
    (["soup","pot"],  "food","🍲","#FF7043"),
    (["burrito","taco"],"food","🌮","#FF8F00"),
    (["spaghetti","pasta","carbonara"],"food","🍝","#FF7043"),
    (["sushi","sashimi"],"food","🍣","#EF5350"),
    (["chocolate","candy","confectionery"],"food","🍫","#5D4037"),
    (["waffle"],     "food","🧇","#FFD54F"),
    (["doughnut","donut"],"food","🍩","#FF9800"),
    (["pancake"],    "food","🥞","#FFCC80"),
    (["cheese"],     "food","🧀","#FFD54F"),
    (["sandwich","club sandwich"],"food","🥪","#FF8F00"),

    (["car","automobile","sedan","convertible","sports car","limousine",
      "jeep","cab","taxi","racer"],    "vehicle","🚗","#42A5F5"),
    (["bus","school bus","trolleybus"],"vehicle","🚌","#FFB300"),
    (["locomotive","train","freight car","electric locomotive"],
     "vehicle","🚂","#EF5350"),
    (["airliner","warplane","biplane","airship"],
     "vehicle","✈️","#5C6BC0"),
    (["bicycle","unicycle"],          "vehicle","🚲","#26A69A"),
    (["motorcycle","motorbike","moped","scooter"],
     "vehicle","🏍️","#8D6E63"),
    (["boat","speedboat","sailboat","canoe","kayak","catamaran","gondola",
      "lifeboat","fireboat"],         "vehicle","⛵","#29B6F6"),
    (["truck","pickup","freight","moving van"],
     "vehicle","🚚","#78909C"),
    (["helicopter"],                  "vehicle","🚁","#FF7043"),
    (["submarine"],                   "vehicle","🚢","#1565C0"),
    (["tank","half track"],           "vehicle","🪖","#546E7A"),
    (["tractor"],                     "vehicle","🚜","#66BB6A"),
    (["ambulance"],                   "vehicle","🚑","#EF5350"),
    (["fire engine"],                 "vehicle","🚒","#EF5350"),
    (["go-kart","golf cart"],         "vehicle","🏎️","#FF7043"),
    (["snowmobile","bobsled"],        "vehicle","🛷","#29B6F6"),

    (["laptop","notebook"],           "object","💻","#78909C"),
    (["cellular","mobile","smartphone","phone"],
     "object","📱","#5C6BC0"),
    (["television","tv","monitor","screen"],
     "object","📺","#37474F"),
    (["book jacket","comic book"],    "object","📚","#8D6E63"),
    (["cup","coffee mug","teacup"],   "object","☕","#FF8A65"),
    (["bottle","water bottle","wine bottle"],
     "object","🍶","#80CBC4"),
    (["clock","watch","digital clock","wall clock","alarm clock","stopwatch","sundial"],
     "object","🕐","#FFA726"),
    (["umbrella","parasol"],          "object","☂️","#7E57C2"),
    (["backpack","rucksack","knapsack"],
     "object","🎒","#EF5350"),
    (["soccer ball","basketball","baseball","volleyball","tennis ball","football","golf ball"],
     "object","⚽","#66BB6A"),
    (["teddy"],                       "object","🧸","#BCAAA4"),
    (["kite"],                        "object","🪁","#FF7043"),
    (["chair","rocking chair","stool"],
     "object","🪑","#8D6E63"),
    (["pencil","ballpoint","fountain pen"],
     "object","✏️","#FDD835"),
    (["guitar","banjo","ukulele"],    "object","🎸","#FF8F00"),
    (["drum","bongo"],                "object","🥁","#EF5350"),
    (["balloon"],                     "object","🎈","#EF5350"),
    (["camera","reflex camera"],      "object","📷","#546E7A"),
    (["microphone"],                  "object","🎤","#FF6B9D"),
    (["violin","cello"],              "object","🎻","#FF8F00"),
    (["piano","organ"],               "object","🎹","#37474F"),
    (["trumpet","trombone","french horn"],
     "object","🎺","#FFD54F"),
    (["flute","oboe","bassoon"],      "object","🎵","#9B5DE5"),
    (["sunglasses"],                  "object","🕶️","#37474F"),
    (["hat","sombrero","cowboy hat"], "object","🎩","#5D4037"),
    (["sock","sandal","shoe","boot","sneaker","loafer"],
     "object","👟","#8D6E63"),
    (["jersey","sweatshirt","lab coat"],
     "object","👕","#42A5F5"),
    (["mask","gas mask"],             "object","😷","#78909C"),
    (["vase","pot"],                  "object","🏺","#FF8F00"),
    (["candle"],                      "object","🕯️","#FFF9C4"),
    (["knife","cleaver"],             "object","🔪","#78909C"),
    (["hammer","wrench","screwdriver"],
     "object","🔨","#78909C"),
    (["lock","padlock"],              "object","🔒","#FFD54F"),
    (["key"],                         "object","🔑","#FFD54F"),
    (["compass","level","rule"],      "object","🧭","#42A5F5"),
    (["bucket","barrel"],             "object","🪣","#42A5F5"),
    (["broom","mop"],                 "object","🧹","#FF8F00"),
    (["toilet","bathtub","shower"],   "object","🚽","#E3F2FD"),
    (["lamp","torch","spotlight"],    "object","💡","#FFD54F"),
    (["envelope","mailbox"],          "object","✉️","#42A5F5"),
    (["telescope","binoculars"],      "object","🔭","#5C6BC0"),
    (["microscope"],                  "object","🔬","#66BB6A"),

    (["tree","oak","palm","pine","maple","willow","banana tree"],
     "nature","🌳","#388E3C"),
    (["flower","rose","daisy","sunflower","tulip","orchid","hibiscus","dahlia","lotus"],
     "nature","🌸","#EC407A"),
    (["cactus","saguaro"],            "nature","🌵","#66BB6A"),
    (["mountain","cliff","valley"],   "nature","🏔️","#78909C"),
    (["volcano"],                     "nature","🌋","#EF5350"),
    (["geyser","fountain"],           "nature","⛲","#29B6F6"),
    (["coral reef","coral"],          "nature","🪸","#FF7043"),
    (["hay","straw"],                 "nature","🌾","#FFD54F"),
]

CAT_DEFAULTS = {
    "animal":  ("📦","#FF9800"),
    "fruit":   ("🍎","#4CAF82"),
    "food":    ("🍽️","#FF5252"),
    "vehicle": ("🚗","#42A5F5"),
    "object":  ("📦","#9B5DE5"),
    "nature":  ("🌿","#66BB6A"),
}

# ── Build keyword → (cat, emoji, color) map ─────────────────────────────────
KW_MAP = {}
for kws, cat, emoji, color in RULES:
    for kw in kws:
        KW_MAP[kw] = (cat, emoji, color)

def classify(raw: str):
    r = raw.lower()
    for kw, info in KW_MAP.items():
        if kw in r:
            return info
    return ("object", "📦", "#78909C")

def clean_name(raw: str) -> str:
    name = raw.split(",")[0].strip()
    name = re.sub(r"\b(a|an|the)\b", "", name)
    return " ".join(w.capitalize() for w in name.split() if w)

# ── Generate dict ────────────────────────────────────────────────────────────
out = {}
for raw in CATS:
    key   = raw.split(",")[0].strip().lower().replace(" ", "_")
    name  = clean_name(raw)
    cat, emoji, color = classify(raw)
    out[key] = {
        "nameEn":   name,
        "nameVn":   name,          # placeholder — user can translate
        "emoji":    emoji,
        "phonetic": "",
        "color":    color,
        "category": cat,
        "funFact":  f"This is a {name.lower()}!",
        "keywords": [raw.split(",")[0].strip().lower()],
    }

with open("imagenet_full.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f"Generated {len(out)} entries -> imagenet_full.json")
print("Tiep theo: doi ten imagenet_full.json thanh imagenet_vn.json")
