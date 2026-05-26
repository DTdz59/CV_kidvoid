import json
from pathlib import Path


TRANSLATION_RULES = {
    # fruit and food
    "apple": "Táo",
    "banana": "Chuối",
    "orange": "Cam",
    "lemon": "Chanh vàng",
    "lime": "Chanh xanh",
    "strawberry": "Dâu tây",
    "pineapple": "Dứa",
    "pomegranate": "Lựu",
    "grape": "Nho",
    "fig": "Quả sung",
    "mushroom": "Nấm",
    "pizza": "Bánh pizza",
    "hamburger": "Bánh hamburger",
    "cheeseburger": "Bánh hamburger phô mai",
    "hot dog": "Bánh mì xúc xích",
    "ice cream": "Kem",
    "ice lolly": "Kem que",
    "cake": "Bánh ngọt",
    "cupcake": "Bánh cupcake",
    "bread": "Bánh mì",
    "bagel": "Bánh mì vòng",
    "baguette": "Bánh mì dài",
    "cookie": "Bánh quy",
    "biscuit": "Bánh quy",
    "pretzel": "Bánh pretzel",
    "espresso": "Cà phê",
    "coffee mug": "Cốc cà phê",
    "teacup": "Tách trà",
    "teapot": "Ấm trà",
    "coffee": "Cà phê",
    "egg": "Trứng",
    "soup": "Súp",
    "sandwich": "Bánh sandwich",
    "taco": "Bánh taco",
    "burrito": "Bánh burrito",
    "spaghetti": "Mì Ý",
    "pasta": "Mì Ý",
    "sushi": "Sushi",
    "chocolate": "Sô cô la",
    "candy": "Kẹo",
    "waffle": "Bánh waffle",
    "doughnut": "Bánh donut",
    "pancake": "Bánh kếp",
    "cheese": "Phô mai",

    # animals
    "dog": "Chó",
    "retriever": "Chó",
    "shepherd": "Chó",
    "poodle": "Chó",
    "terrier": "Chó",
    "husky": "Chó",
    "bulldog": "Chó",
    "beagle": "Chó",
    "pug": "Chó",
    "chihuahua": "Chó",
    "dachshund": "Chó",
    "spaniel": "Chó",
    "samoyed": "Chó",
    "collie": "Chó",
    "boxer": "Chó",
    "rottweiler": "Chó",
    "greyhound": "Chó",
    "cat": "Mèo",
    "kitten": "Mèo con",
    "tabby": "Mèo",
    "persian": "Mèo",
    "siamese": "Mèo",
    "fish": "Cá",
    "goldfish": "Cá vàng",
    "shark": "Cá mập",
    "great white": "Cá mập trắng",
    "tiger shark": "Cá mập hổ",
    "hammerhead": "Cá mập đầu búa",
    "stingray": "Cá đuối",
    "ray": "Cá đuối",
    "eel": "Lươn",
    "salmon": "Cá hồi",
    "puffer": "Cá nóc",
    "bird": "Chim",
    "robin": "Chim cổ đỏ",
    "sparrow": "Chim sẻ",
    "finch": "Chim sẻ",
    "crow": "Quạ",
    "raven": "Quạ",
    "eagle": "Đại bàng",
    "hawk": "Diều hâu",
    "owl": "Cú mèo",
    "peacock": "Công",
    "parrot": "Vẹt",
    "macaw": "Vẹt",
    "ostrich": "Đà điểu",
    "hen": "Gà mái",
    "cock": "Gà trống",
    "rooster": "Gà trống",
    "chicken": "Gà",
    "duck": "Vịt",
    "goose": "Ngỗng",
    "penguin": "Chim cánh cụt",
    "snake": "Rắn",
    "python": "Trăn",
    "cobra": "Rắn hổ mang",
    "viper": "Rắn lục",
    "turtle": "Rùa",
    "tortoise": "Rùa cạn",
    "frog": "Ếch",
    "toad": "Cóc",
    "lizard": "Thằn lằn",
    "iguana": "Kỳ nhông",
    "gecko": "Tắc kè",
    "chameleon": "Tắc kè hoa",
    "spider": "Nhện",
    "scorpion": "Bọ cạp",
    "tarantula": "Nhện lớn",
    "butterfly": "Bướm",
    "bee": "Ong",
    "ant": "Kiến",
    "dragonfly": "Chuồn chuồn",
    "beetle": "Bọ cánh cứng",
    "cockroach": "Gián",
    "elephant": "Voi",
    "lion": "Sư tử",
    "tiger": "Hổ",
    "bear": "Gấu",
    "panda": "Gấu trúc",
    "monkey": "Khỉ",
    "gorilla": "Khỉ đột",
    "chimpanzee": "Tinh tinh",
    "rabbit": "Thỏ",
    "hare": "Thỏ rừng",
    "horse": "Ngựa",
    "zebra": "Ngựa vằn",
    "cow": "Bò",
    "ox": "Bò",
    "bull": "Bò đực",
    "buffalo": "Trâu",
    "pig": "Lợn",
    "boar": "Lợn rừng",
    "sheep": "Cừu",
    "goat": "Dê",
    "deer": "Hươu",
    "camel": "Lạc đà",
    "llama": "Lạc đà không bướu",
    "wolf": "Sói",
    "fox": "Cáo",
    "leopard": "Báo",
    "cheetah": "Báo săn",
    "jaguar": "Báo đốm",
    "rhinoceros": "Tê giác",
    "hippopotamus": "Hà mã",
    "giraffe": "Hươu cao cổ",
    "kangaroo": "Chuột túi",
    "crab": "Cua",
    "lobster": "Tôm hùm",
    "jellyfish": "Sứa",
    "starfish": "Sao biển",

    # vehicles
    "car": "Ô tô",
    "automobile": "Ô tô",
    "taxi": "Taxi",
    "cab": "Taxi",
    "jeep": "Xe jeep",
    "limousine": "Xe limousine",
    "racer": "Xe đua",
    "bus": "Xe buýt",
    "school bus": "Xe buýt trường học",
    "train": "Tàu hỏa",
    "locomotive": "Đầu máy xe lửa",
    "airliner": "Máy bay",
    "airplane": "Máy bay",
    "warplane": "Máy bay quân sự",
    "bicycle": "Xe đạp",
    "motorcycle": "Xe máy",
    "scooter": "Xe tay ga",
    "boat": "Thuyền",
    "sailboat": "Thuyền buồm",
    "canoe": "Ca nô",
    "kayak": "Thuyền kayak",
    "truck": "Xe tải",
    "pickup": "Xe bán tải",
    "ambulance": "Xe cứu thương",
    "fire engine": "Xe cứu hỏa",
    "tractor": "Máy kéo",
    "helicopter": "Trực thăng",
    "submarine": "Tàu ngầm",
    "dogsled": "Xe trượt tuyết chó kéo",

    # objects
    "backpack": "Ba lô",
    "rucksack": "Ba lô",
    "book": "Sách",
    "book jacket": "Bìa sách",
    "comic": "Truyện tranh",
    "laptop": "Máy tính xách tay",
    "notebook": "Máy tính xách tay",
    "computer": "Máy tính",
    "cellular telephone": "Điện thoại di động",
    "mobile phone": "Điện thoại di động",
    "phone": "Điện thoại",
    "television": "Tivi",
    "monitor": "Màn hình",
    "screen": "Màn hình",
    "camera": "Máy ảnh",
    "clock": "Đồng hồ",
    "watch": "Đồng hồ đeo tay",
    "stopwatch": "Đồng hồ bấm giờ",
    "umbrella": "Ô",
    "parasol": "Dù che",
    "soccer ball": "Bóng đá",
    "basketball": "Bóng rổ",
    "baseball": "Bóng chày",
    "tennis ball": "Bóng tennis",
    "volleyball": "Bóng chuyền",
    "golf ball": "Bóng golf",
    "teddy": "Gấu bông",
    "chair": "Ghế",
    "stool": "Ghế đẩu",
    "rocking chair": "Ghế bập bênh",
    "cup": "Cốc",
    "mug": "Cốc",
    "bottle": "Chai",
    "water bottle": "Chai nước",
    "wine bottle": "Chai rượu",
    "pencil": "Bút chì",
    "pen": "Bút",
    "ballpoint": "Bút bi",
    "key": "Chìa khóa",
    "lock": "Ổ khóa",
    "padlock": "Ổ khóa",
    "hammer": "Búa",
    "wrench": "Cờ lê",
    "screwdriver": "Tua vít",
    "knife": "Dao",
    "cleaver": "Dao chặt",
    "lamp": "Đèn",
    "torch": "Đèn pin",
    "envelope": "Phong bì",
    "mailbox": "Hộp thư",
    "balloon": "Bóng bay",
    "sunglasses": "Kính râm",
    "hat": "Mũ",
    "sombrero": "Mũ rộng vành",
    "shoe": "Giày",
    "sneaker": "Giày thể thao",
    "boot": "Ủng",
    "sandal": "Dép xăng đan",
    "sock": "Tất",
    "shirt": "Áo",
    "jersey": "Áo thể thao",
    "sweatshirt": "Áo nỉ",
    "lab coat": "Áo blouse",
    "toilet": "Bồn cầu",
    "bathtub": "Bồn tắm",
    "shower": "Vòi sen",
    "vase": "Bình hoa",
    "pot": "Nồi",
    "bucket": "Xô",
    "barrel": "Thùng",
    "broom": "Chổi",
    "mop": "Cây lau nhà",
    "guitar": "Đàn guitar",
    "piano": "Đàn piano",
    "drum": "Trống",
    "microphone": "Micro",
    "violin": "Đàn violin",
    "cello": "Đàn cello",
    "trumpet": "Kèn trumpet",
    "flute": "Sáo",
    "mask": "Mặt nạ",
    "candle": "Nến",
    "telescope": "Kính thiên văn",
    "binoculars": "Ống nhòm",
    "microscope": "Kính hiển vi",
    "compass": "La bàn",

    # nature
    "tree": "Cây",
    "oak": "Cây sồi",
    "palm": "Cây cọ",
    "pine": "Cây thông",
    "flower": "Hoa",
    "rose": "Hoa hồng",
    "daisy": "Hoa cúc",
    "sunflower": "Hoa hướng dương",
    "cactus": "Xương rồng",
    "mountain": "Núi",
    "cliff": "Vách đá",
    "volcano": "Núi lửa",
    "fountain": "Đài phun nước",
    "geyser": "Mạch nước phun",
    "coral": "San hô",
}


CATEGORY_FALLBACKS = {
    "animal": "Động vật",
    "fruit": "Trái cây",
    "food": "Đồ ăn",
    "vehicle": "Phương tiện",
    "object": "Đồ vật",
    "nature": "Thiên nhiên",
}

GENERIC_EXACT_PREFIXES = {
    "Chó": "Chó",
    "Mèo": "Mèo",
    "Chim": "Chim",
    "Cá": "Cá",
    "Rắn": "Rắn",
    "Ếch": "Ếch",
    "Rùa": "Rùa",
    "Thằn lằn": "Thằn lằn",
    "Nhện": "Nhện",
    "Cua": "Cua",
    "Vẹt": "Vẹt",
    "Gà": "Gà",
    "Vịt": "Vịt",
    "Ngỗng": "Ngỗng",
    "Bò": "Bò",
    "Lợn": "Lợn",
    "Cừu": "Cừu",
    "Dê": "Dê",
    "Khỉ": "Khỉ",
    "Côn trùng": "Côn trùng",
}

SPECIFIC_PREFIX_RULES = [
    ([
        "dog", "retriever", "shepherd", "poodle", "terrier", "husky", "bulldog",
        "dalmatian", "corgi", "beagle", "pug", "chihuahua", "dachshund",
        "spaniel", "samoyed", "malamute", "collie", "boxer", "rottweiler",
        "greyhound", "whippet", "bloodhound", "basset", "doberman",
        "schnauzer", "chow", "pekinese", "shih", "papillon", "borzoi",
        "saluki", "afghan", "leonberg", "newfoundland", "saint bernard",
        "appenzeller", "entlebucher", "griffon",
    ], "Chó"),
    ([
        "cat", "kitten", "tabby", "persian", "siamese", "egyptian", "angora",
    ], "Mèo"),
    ([
        "tench", "goldfish", "fish", "shark", "ray", "stingray", "eel",
        "salmon", "coho", "sturgeon", "gar", "lionfish", "puffer",
    ], "Cá"),
    ([
        "brambling", "finch", "junco", "bunting", "robin", "bulbul", "jay",
        "magpie", "chickadee", "ouzel", "kite", "eagle", "vulture", "owl",
        "grouse", "ptarmigan", "quail", "partridge", "peacock", "macaw",
        "cockatoo", "lorikeet", "coucal", "bee eater", "hornbill",
        "hummingbird", "jacamar", "toucan", "drake", "merganser", "goose",
        "swan", "ostrich", "hen", "cock", "rooster", "chicken",
    ], "Chim"),
    ([
        "salamander", "newt", "eft", "axolotl",
    ], "Kỳ giông"),
    ([
        "frog", "bullfrog", "toad",
    ], "Ếch"),
    ([
        "turtle", "tortoise", "terrapin",
    ], "Rùa"),
    ([
        "gecko", "iguana", "chameleon", "lizard", "agama", "gila monster",
        "komodo dragon",
    ], "Thằn lằn"),
    ([
        "crocodile", "alligator",
    ], "Cá sấu"),
    ([
        "snake", "python", "cobra", "mamba", "viper", "diamondback",
        "sidewinder", "boa",
    ], "Rắn"),
    ([
        "spider", "tarantula", "widow",
    ], "Nhện"),
    ([
        "beetle", "ladybug", "weevil",
    ], "Bọ cánh cứng"),
    ([
        "butterfly", "monarch",
    ], "Bướm"),
    ([
        "bee", "ant", "dragonfly", "damselfly", "mantis", "cricket",
        "cockroach", "grasshopper", "leafhopper", "lacewing", "fly",
        "mosquito", "tick", "centipede",
    ], "Côn trùng"),
    ([
        "crab", "lobster", "crayfish",
    ], "Cua/tôm"),
    ([
        "jellyfish", "anemone", "coral", "starfish", "urchin", "slug",
        "snail", "conch", "chiton", "nautilus",
    ], "Sinh vật biển"),
    ([
        "monkey", "macaque", "chimpanzee", "gorilla", "orangutan", "gibbon",
        "baboon", "marmoset", "colobus", "proboscis", "lemur", "indri",
    ], "Linh trưởng"),
    ([
        "horse", "zebra", "cow", "ox", "bull", "buffalo", "bison", "ram",
        "sheep", "goat", "deer", "antelope", "gazelle", "impala", "camel",
        "llama", "alpaca", "pig", "boar", "hog", "warthog",
    ], "Động vật"),
    ([
        "car", "automobile", "taxi", "cab", "jeep", "limousine", "racer",
        "bus", "locomotive", "train", "airliner", "airplane", "warplane",
        "bicycle", "motorcycle", "scooter", "boat", "sailboat", "canoe",
        "kayak", "truck", "pickup", "ambulance", "fire engine", "tractor",
        "helicopter", "submarine", "tank",
    ], "Phương tiện"),
    ([
        "apple", "banana", "orange", "lemon", "lime", "strawberry",
        "pineapple", "pomegranate", "grape", "fig", "granny smith",
    ], "Trái cây"),
]


def _clean_for_vn(name: str) -> str:
    return name.replace(" And ", " and ").replace(" Of ", " of ")


def _text_for_match(key: str, obj: dict) -> str:
    return " ".join([
        key.replace("_", " "),
        obj.get("nameEn", ""),
        " ".join(obj.get("keywords", [])),
    ]).lower()


def _exact_translation(key: str, obj: dict) -> str | None:
    candidates = [
        key.replace("_", " ").lower(),
        (obj.get("nameEn") or "").strip().lower(),
        *[kw.lower() for kw in obj.get("keywords", [])],
    ]
    for candidate in candidates:
        if candidate in TRANSLATION_RULES:
            return TRANSLATION_RULES[candidate]
    return None


def find_translation(key: str, obj: dict) -> str:
    exact = _exact_translation(key, obj)
    name_en = _clean_for_vn(obj.get("nameEn") or key.replace("_", " ").title())
    if exact:
        if exact in GENERIC_EXACT_PREFIXES:
            if name_en.lower() in {"dog", "cat", "bird", "fish", "snake", "frog", "turtle"}:
                return exact
            return f"{GENERIC_EXACT_PREFIXES[exact]} {name_en}"
        return exact

    text = _text_for_match(key, obj)

    for keywords, prefix in SPECIFIC_PREFIX_RULES:
        if any(keyword in text for keyword in keywords):
            return f"{prefix} {name_en}"

    if obj.get("category") == "object":
        return name_en
    if obj.get("category") == "animal":
        return name_en
    if obj.get("category") == "food":
        return name_en
    if obj.get("category") == "vehicle":
        return name_en
    if obj.get("category") == "nature":
        return name_en
    if obj.get("category") == "fruit":
        return name_en
    return name_en


def main():
    path = Path("imagenet_vn.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = 0

    for key, obj in data.items():
        old = (obj.get("nameVn") or "").strip()
        en = (obj.get("nameEn") or "").strip()
        fake_prefixes = (
            "Đồ vật ", "Động vật ", "Phương tiện ",
            "Đồ ăn ", "Thiên nhiên ", "Trái cây ",
        )
        needs_update = (
            not old
            or old.lower() == en.lower()
            or old in CATEGORY_FALLBACKS.values()
            or old.startswith(fake_prefixes)
        )
        if not needs_update:
            continue

        new = find_translation(key, obj)
        if new and new != old:
            obj["nameVn"] = new
            changed += 1

    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Updated {changed} Vietnamese names in {path}")


if __name__ == "__main__":
    main()
