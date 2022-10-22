import asyncio

FLOORS = 5
ELEVATORS = 2
PEOPLE = 10
STAR_FLOOR = 1
PROBABILITY = {
    'min': 1,
    'max': FLOORS,
    'step': 1,
    'probability': [{
        'value': 1,
        'probability': 0.8
    }] + [{
        'value': x,
        'probability': 0.2 / ((FLOORS - 1) ^ 2) * (x - 1) * (FLOORS - x)
    } for x in range(2, FLOORS)]
}
LOOP = asyncio.get_event_loop()
ALGORITHIM = "random"
VERBOSE = False