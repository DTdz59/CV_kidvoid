import json
from pathlib import Path


MANUAL_FIXES = {
    "triceratops": "Khủng long ba sừng",
    "loggerhead": "Rùa Loggerhead",
    "wallaby": "Chuột túi Wallaby",
    "weimaraner": "Chó Weimaraner",
    "airedale": "Chó Airedale",
    "cairn": "Chó Cairn Terrier",
    "dandie_dinmont": "Chó Dandie Dinmont Terrier",
    "lhasa": "Chó Lhasa Apso",
    "vizsla": "Chó Vizsla",
    "gordon_setter": "Chó Gordon Setter",
    "clumber": "Chó Clumber Spaniel",
    "kuvasz": "Chó Kuvasz",
    "schipperke": "Chó Schipperke",
    "groenendael": "Chó Groenendael",
    "briard": "Chó Briard",
    "kelpie": "Chó Kelpie",
    "komondor": "Chó Komondor",
    "bouvier_des_flandres": "Chó Bouvier des Flandres",
    "basenji": "Chó Basenji",
    "keeshond": "Chó Keeshond",
    "pembroke": "Chó Pembroke Welsh Corgi",
    "meerkat": "Cầy meerkat",
    "lynx": "Linh miêu",
    "lycaenid": "Bướm Lycaenid",
    "marmot": "Sóc marmot",
    "armadillo": "Tatu",
    "guenon": "Khỉ Guenon",
    "titi": "Khỉ Titi",
    "abaya": "Áo choàng abaya",
    "bannister": "Lan can",
    "barrow": "Xe cút kít",
    "bassoon": "Kèn bassoon",
    "bikini": "Đồ bơi bikini",
    "caldron": "Vạc",
    "cornet": "Kèn cornet",
    "cuirass": "Áo giáp ngực",
    "ipod": "Máy nghe nhạc iPod",
    "jean": "Quần jean",
    "jinrikisha": "Xe kéo tay",
    "kimono": "Áo kimono",
    "maraca": "Nhạc cụ maraca",
    "marimba": "Đàn marimba",
    "maypole": "Cột lễ hội Maypole",
    "modem": "Bộ modem",
    "pickelhaube": "Mũ Pickelhaube",
    "puck": "Bóng khúc côn cầu",
    "radio": "Đài radio",
    "shoji": "Cửa giấy shoji",
    "trimaran": "Thuyền ba thân",
    "yurt": "Lều yurt",
    "buckeye": "Hạt dẻ ngựa buckeye",
    "bolete": "Nấm bolete",
    "warthog": "Lợn bướu",
    "impala": "Linh dương Impala",
    "hay": "Cỏ khô",
    "gyromitra": "Nấm Gyromitra",
    "bicycle-built-for-two": "Xe đạp đôi",
}


def main():
    path = Path("imagenet_vn.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    for key, value in MANUAL_FIXES.items():
        if key in data:
            data[key]["nameVn"] = value
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Applied {len(MANUAL_FIXES)} manual Vietnamese name fixes")


if __name__ == "__main__":
    main()
