#!/usr/bin/env python3
"""
Neo Geo CMC42/CMC50 用  M1(Z80)ROM 内「スプライト復号用データ」の読み出し/埋め込みツール
FBNeo neo_decrypt.cpp の NeoCMCGetXorData / NeoCMCGetExtraXor の仕様に基づく。

  python3 neo_cmc_xordata.py read  m1.bin
  python3 neo_cmc_xordata.py embed m1.bin m1_out.bin [--flags 0x32 --extra 0xfe --u1 0x4d --u2 0x68] [--force]

既定値は S1945P (CMC42): 32, fe, 4d, 68。  --game kof99 などでFBNeoの表のプリセットを使用
(CMC50 の場合は u1=0x2b, u2=0xa9 を指定)
"""
import sys, random, argparse

BASE = 0xF9A0
# (address_bits, address_xor) のペア。FBNeoの呼び出しと同じ並び
SLOTS = {
    "flags": [(0x16, 0x0a), (0x1e, 0x1c)],
    "extra": [(0x10, 0x04), (0x1a, 0x18)],
    "u1":    [(0x0c, 0x00), (0x0e, 0x06)],
    "u2":    [(0x12, 0x02), (0x14, 0x08)],
}


# FBNeo neo_decrypt.cpp の表より (flags, extra(=MAME値^0xfb/^0x5c), u1, u2)
PRESETS = {
    "bangbead": (0x02,0x03,0x4d,0x68), "ganryu": (0x02,0xfc,0x4d,0x68),
    "garou": (0x33,0xfd,0x4d,0x68), "mslug3": (0x33,0x56,0x4d,0x68),
    "nitd": (0x02,0x04,0x4d,0x68), "preisle2": (0x22,0x64,0x4d,0x68),
    "sengoku3": (0x12,0x05,0x4d,0x68), "s1945p": (0x32,0xfe,0x4d,0x68),
    "kof99": (0x32,0xfb,0x4d,0x68), "zupapa": (0x02,0x46,0x4d,0x68),
    # CMC50 (M1自体も暗号化が必要)
    "jockeygp": (0x02,0xf0,0x2b,0xa9), "matrim": (0x3a,0x36,0x2b,0xa9),
    "mslug4": (0x23,0x6d,0x2b,0xa9), "mslug5": (0x32,0x45,0x2b,0xa9),
    "pnyaa": (0x02,0x72,0x2b,0xa9), "rotd": (0x32,0x63,0x2b,0xa9),
    "samsho5": (0x32,0x53,0x2b,0xa9), "samsho5sp": (0x32,0x51,0x2b,0xa9),
    "svc": (0x3a,0x0b,0x2b,0xa9), "kof2000": (0x3a,0x5c,0x2b,0xa9),
    "kof2001": (0x32,0x42,0x2b,0xa9), "kof2002": (0x32,0xb0,0x2b,0xa9),
    "kof2003": (0x3a,0xc1,0x2b,0xa9),
}

def get_xor_data(m1, bits, xr):
    a  = m1[BASE+bits] | (m1[BASE+bits+1] << 8)
    a ^= (m1[BASE+xr] << 8) | m1[BASE+xr+1]
    a = ((a & 0x8000) >> 15) | ((a & 0x7fff) << 1)
    return m1[a], a

def read_all(m1):
    out = {}
    for name, ((b1, x1), (b2, x2)) in SLOTS.items():
        v1, a1 = get_xor_data(m1, b1, x1)
        v2, a2 = get_xor_data(m1, b2, x2)
        out[name] = (v1 ^ v2, a1, a2)
    return out

def embed(m1, vals, force=False, seed=None):
    rnd = random.Random(seed)
    m1 = bytearray(m1)
    if len(m1) < 0x10000:
        m1 += b"\xff" * (0x10000 - len(m1))
    # 0xF800-0xFFFF は Z80 RAM 領域でROMとしては使われない領域
    ptr_area = list(range(BASE, BASE + 0x20))
    fill = m1[BASE]
    # 実ROMで使われている 0xF800-0xFBFF 領域(ポインタ領域を除く)から空きバイトを選ぶ
    cand = [a for a in range(0xF800, 0xFC00) if a not in ptr_area and m1[a] == fill]
    if not force:
        if any(m1[a] != fill for a in ptr_area):
            raise SystemExit("0xF9A0-0xF9BF に既存データあり。--force で上書き")
        if len(cand) < 8:
            raise SystemExit("0xF800-0xFBFF に空き領域が足りません。--force で上書き")
    else:
        cand = [a for a in range(0xF800, 0xFC00) if a not in ptr_area]
    addrs = rnd.sample(cand, 8)
    k = 0
    for name, ((b1, x1), (b2, x2)) in SLOTS.items():
        target = vals[name]
        for (bits, xr), v in zip(((b1, x1), (b2, x2)), (target, 0x00)):
            A = addrs[k]; k += 1
            m1[A] = v
            raw = (A >> 1) | ((A & 1) << 15)      # 回転の逆
            p1 = rnd.randrange(0x10000)
            p2 = raw ^ p1
            m1[BASE+bits]   = p1 & 0xff
            m1[BASE+bits+1] = p1 >> 8
            m1[BASE+xr]     = p2 >> 8
            m1[BASE+xr+1]   = p2 & 0xff
    return bytes(m1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["read", "embed", "selftest"])
    ap.add_argument("src", nargs="?"); ap.add_argument("dst", nargs="?")
    ap.add_argument("--flags", type=lambda s: int(s, 0), default=None)
    ap.add_argument("--extra", type=lambda s: int(s, 0), default=None)
    ap.add_argument("--u1",    type=lambda s: int(s, 0), default=0x4d)
    ap.add_argument("--u2",    type=lambda s: int(s, 0), default=0x68)
    ap.add_argument("--game", choices=sorted(PRESETS), help="FBNeoの表のプリセット(個別指定が優先)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    base = PRESETS[a.game] if a.game else PRESETS["s1945p"]
    vals = {k: (getattr(a, k) if getattr(a, k) is not None else base[i])
            for i, k in enumerate(("flags", "extra", "u1", "u2"))}
    if a.mode == "selftest":
        m = embed(b"\x00" * 0x10000, vals, seed=1)
        r = read_all(m)
        ok = all(r[k][0] == vals[k] for k in vals)
        print({k: hex(v[0]) for k, v in r.items()}, "OK" if ok else "NG")
        sys.exit(0 if ok else 1)
    m1 = open(a.src, "rb").read()
    if a.mode == "read":
        for k, (v, a1, a2) in read_all(m1).items():
            print(f"{k:6s} = 0x{v:02X}   (読み出し先 0x{a1:04X}, 0x{a2:04X})")
        print(f"CMC42のOLDXOR換算: extra^0xfb = 0x{read_all(m1)['extra'][0]^0xfb:02X}  / CMC50: extra^0x5c = 0x{read_all(m1)['extra'][0]^0x5c:02X}")
    else:
        out = embed(m1, vals, a.force, a.seed)
        open(a.dst, "wb").write(out)
        print("書き込み後の読み戻し:", {k: hex(v[0]) for k, v in read_all(out).items()})
if __name__ == "__main__":
    main()