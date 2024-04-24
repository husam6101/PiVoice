import platform

if platform.system() != "Windows":
    import board

    gpio_to_pin_map = {
        2: board.D2,
        3: board.D3,
        4: board.D4,
        14: board.D14,
        15: board.D15,
        17: board.D17,
        18: board.D18,
        27: board.D27,
        22: board.D22,
        23: board.D23,
        24: board.D24,
        10: board.D10,
        9: board.D9,
        25: board.D25,
        11: board.D11,
        8: board.D8,
        7: board.D7,
        0: board.D0,
        1: board.D1,
        5: board.D5,
        6: board.D6,
        12: board.D12,
        13: board.D13,
        19: board.D19,
        16: board.D16,
        26: board.D26,
        20: board.D20,
        21: board.D21,
    }
else:
    gpio_to_pin_map = {
        2: 3,
        3: 5,
        4: 7,
        14: 8,
        15: 10,
        17: 11,
        18: 12,
        27: 13,
        22: 15,
        23: 16,
        24: 18,
        10: 19,
        9: 21,
        25: 22,
        11: 23,
        8: 24,
        7: 26,
        0: 27,
        1: 28,
        5: 29,
        6: 31,
        12: 32,
        13: 33,
        19: 35,
        16: 36,
        26: 37,
        20: 38,
        21: 40,
    }
