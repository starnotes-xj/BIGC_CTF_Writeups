"""
CPCTF - Anomaly 2

N 的十进制形式是 1^a 0^b 7^a。根据提示给出的乘法结构：

    11111 * 1000007 = 11111077777

一般化可得：

    1^a 0^b 7^a = ((10^a - 1) // 9) * (10^(a+b) + 7)

因此无需通用分解算法，直接构造 p, q 后做标准 RSA 解密即可。
"""

from __future__ import annotations

import re
from pathlib import Path


ATTACHMENT = (
    Path(__file__).resolve().parents[1]
    / "files"
    / "Anomaly_2"
    / "107107_b38e4b4bcd49c22b496049abb867695331cdc0f7542dd59288b3597e1b8e4119.txt"
)


def parse_attachment(path: Path) -> tuple[int, int, int]:
    text = path.read_text()
    values: dict[str, int] = {}
    for name in ("N", "e", "c"):
        match = re.search(rf"{name}\s*=\s*(\d+)", text)
        if match is None:
            raise ValueError(f"附件中找不到 {name}")
        values[name] = int(match.group(1))
    return values["N"], values["e"], values["c"]


def split_digit_runs(n: int) -> tuple[int, int, int]:
    digits = str(n)
    match = re.fullmatch(r"(1+)(0+)(7+)", digits)
    if match is None:
        raise ValueError("N 不是 1^a 0^b 7^a 的形式")

    ones, zeros, sevens = map(len, match.groups())
    if ones != sevens:
        raise ValueError("N 中 1 和 7 的数量不同，无法套用本题结构")
    return ones, zeros, sevens


def long_to_bytes(n: int) -> bytes:
    return n.to_bytes((n.bit_length() + 7) // 8, "big")


def solve() -> str:
    n, e, c = parse_attachment(ATTACHMENT)
    ones, zeros, _ = split_digit_runs(n)

    p = (10**ones - 1) // 9
    q = 10 ** (ones + zeros) + 7
    if p * q != n:
        raise ValueError("构造出的 p, q 无法还原 N")

    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    m = pow(c, d, n)
    return long_to_bytes(m).decode()


def main() -> None:
    print(solve())


if __name__ == "__main__":
    main()
