#!/usr/bin/env python3
"""Arithmetic sanity checks for the SRG examples recovered in README.md.

This does NOT prove nonexistence. It only checks that the printed tuples satisfy
the standard strongly-regular parameter identity and that the complement formula
is internally consistent.
"""

EXAMPLES = [
    (21, 10, 4, 5),
    (28, 9, 0, 4),
    (33, 16, 7, 8),
    (49, 16, 3, 6),
    (50, 21, 4, 12),
    (56, 22, 3, 12),
    (57, 28, 13, 14),
    (64, 30, 18, 10),
    (69, 34, 16, 17),
    (75, 32, 10, 16),
    (76, 21, 2, 7),
    (76, 30, 8, 14),
    (77, 38, 18, 19),
    (93, 46, 22, 23),
    (95, 40, 12, 20),
    (96, 38, 10, 18),
    (96, 45, 24, 18),
]


def feasible_identity(v, k, lam, mu):
    return (v - k - 1) * mu == k * (k - lam - 1)


def complement(t):
    v, k, lam, mu = t
    return (
        v,
        v - k - 1,
        v - 2 * k + mu - 2,
        v - 2 * k + lam,
    )


def main():
    assert len(EXAMPLES) == 17
    assert len(set(EXAMPLES)) == len(EXAMPLES)
    for t in EXAMPLES:
        assert feasible_identity(*t), t
        c = complement(t)
        assert feasible_identity(*c), (t, c)
        assert complement(c) == t, (t, c, complement(c))
    print('PASS')
    print(f'recovered_examples={len(EXAMPLES)}')
    print('all satisfy (v-k-1)mu = k(k-lambda-1)')
    print('complement map is involutive on all listed examples')
    print('NOTE: arithmetic feasibility is not an existence/nonexistence proof')


if __name__ == '__main__':
    main()
