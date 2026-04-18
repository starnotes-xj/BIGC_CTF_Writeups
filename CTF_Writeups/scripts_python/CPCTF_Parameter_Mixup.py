import math
import random


N1 = 87405182736104359780257026883853062930574663561980633775939752446259523158955808889602775147349422181286752422777444540409043705137242444906859982710084376976995577762838755152310969883588687143185855446868518299103284219288298089004723615989669846760852206531362806473299208237879292642911953181354015637739
C1 = 5947050188011198882167638654472754073461946759644146614025932625290616486683809
N2 = 89984079446277129336031962353513290766726794253576464892005498900113523905864088594103793620450760604852463679010581777863799208215048737093285826288578917592161127386371969728330753862369184707806787782705755694366125100020912792307994059926523686129099696784648345246590104006734129991238410853485925459399
C2 = 1469764391126334007675223493311131828227376713240295689831327636992622204657369


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)
    for p in small_primes:
        if n % p == 0:
            return n == p

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def pollard_rho(n: int) -> int:
    if n % 2 == 0:
        return 2

    while True:
        x = random.randrange(2, n - 1)
        y = x
        c = random.randrange(1, n - 1)
        d = 1
        while d == 1:
            x = (pow(x, 2, n) + c) % n
            y = (pow(y, 2, n) + c) % n
            y = (pow(y, 2, n) + c) % n
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d


def factor(n: int, out: list[int]) -> None:
    if n == 1:
        return
    if is_probable_prime(n):
        out.append(n)
        return
    d = pollard_rho(n)
    factor(d, out)
    factor(n // d, out)


def to_bytes(n: int) -> bytes:
    if n == 0:
        return b"\x00"
    return n.to_bytes((n.bit_length() + 7) // 8, "big")


def main() -> None:
    g = math.gcd(N1**3 - C1, N2**3 - C2)
    factors: list[int] = []
    factor(g, factors)
    factors.sort()

    print(f"g = {g}")
    print(f"factors = {factors}")

    seen = set()
    for mask in range(1, 1 << len(factors)):
        candidate = 1
        for i, prime in enumerate(factors):
            if mask >> i & 1:
                candidate *= prime
        if candidate in seen:
            continue
        seen.add(candidate)

        data = to_bytes(candidate)
        if data.startswith(b"CPCTF{"):
            print(data.decode())
            return

    raise RuntimeError("flag not found")


if __name__ == "__main__":
    main()
