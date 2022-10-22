from random import random
from tabnanny import check
import time
import math
import asyncio
from helpers import setTimeout, cprint, timestamp
from constants import *

TERMINATE = [False, False]

class Probability():

    class ProbabilityEntry():
        def __init__(self, probability, value):
            self.probability = probability
            self.value = value

    def __init__(self, prob):
        self.min = prob['min']
        self.max = prob['max']
        self.discrete = prob.get('discrete', False)
        self.step = prob.get('step', 1)

        tmp_sum = sum([float(x['probability']) for x in prob['probability']])
        self.probabilites = [Probability.ProbabilityEntry(x['probability'] / tmp_sum, x['value']) for x in prob['probability']]
        self.probabilites.sort(key=lambda x: x.probability, reverse=True)

    def rand(self):
        r = random()
        for p in self.probabilites:
            if r <= p.probability:
                return p.value
            r -= p.probability
        return self.probabilites[-1].value

    def rand_unique(self, count, default=None):
        # get count unique random values
        values = []
        if (default is not None):
            values.append(default)
            count -= 1
        for i in range(count):
            value = self.rand()
            while value in values:
                value = self.rand()
            values.append(value)
        return values

class Passenger():
    def __init__(self, id, start, end, random=random):
        self.id = id
        self.origin = start
        self.destination = end

        if start == end:
            raise ValueError('Passenger cannot have same origin and destination')

        if not callable(random):
            if random == "Gaussian":
                self.random = lambda: math.ceil(abs(random.gauss(10000, 1000)))
            elif random == "Uniform":
                self.random = lambda: math.ceil(random.uniform(10000, 100000))
            elif random == "Discrete":
                self.random = lambda: math.ceil(random.randint(10000, 100000))
            elif random == "Exponential":
                self.random = lambda: math.ceil(random.expovariate(1/10000))
            else:
                self.random = math.ceil(random.random() * 100000)
        else:
            self.random = random

        self.probability = Probability(PROBABILITY)

        cprint(f'DECLARATION: Passenger {self.id} created', 'magenta')


    def gen_passengers(self, count, start, end):
        return [Passenger(i, start.rand(), end.rand()) for i in range(count)]

    def dropped(self):
        if self.origin == self.destination and self.origin == STAR_FLOOR:
            building.remove_passenger(self)
        return True

    def move(self):
        self.destination = list(filter(lambda x: x != self.origin, self.probability.rand_unique(2, default=self.origin)))[0]
        print(f'Passenger {self.id} moved from {self.origin} to {self.destination}')

    def run(self):
        while self.origin != self.destination:
            continue
        time_to_move = self.random() / 100
        setTimeout(time_to_move, self.move)

class Floor(object):
    def __init__(self, passengers_count, floor):
        self.passengers_count = passengers_count
        self.passengers = set()
        self.floor = floor

        cprint(f'DECLARATION: Floor {self.floor} created', 'magenta')

    def add_passenger(self, passenger):
        self.passengers.add(passenger)

    def remove_passenger(self, passenger):
        self.passengers.remove(passenger)

    def check_floor(self):
        return {
            "len": len(self.passengers),
            "passengers": self.passengers
        }

class Elevator(object):
    def __init__(self, id, floors, capacity, speed, door_delay, passenger_idle_time, current_floor = 1):
        self.id = id
        self.floors = floors
        self.capacity = capacity
        self.speed = speed                # ms per floor
        self.current_floor = current_floor
        self.passenagers = set()
        self.direction = 1                # 1 = up, -1 = down, 0 is idle
        self.available = True
        self.queue = set()
        self.door_delay = door_delay
        self.passenger_idle_time = passenger_idle_time
        self.time = 0

        cprint(f'DECLARATION: Elevator {self.id} created', 'magenta')

    def queue(self, floor):
        self.queue.add(floor)

    def add_passenger(self, passenger):
        if passenger.destination == passenger.origin:
            return
        elif (self.capacity - len(self.passenagers)) > 0:
            self.passenagers.add(passenger)
            self.queue.add(passenger.destination)

    def sleep(self, time):
        self.time += time

    def open_door(self, sleep_time = 1000):
        print("ELEVATOR {}: Opening door on floor {}".format(self.id, self.current_floor))
        self.sleep(sleep_time)

    def close_door(self, sleep_time = 1000):
        print("ELEVATOR {}: Closing door on floor {}".format(self.id, self.current_floor))
        self.sleep(sleep_time)

    def drop_passengers(self):
        for passenger in self.passenagers:
            if passenger.destination == self.current_floor:
                self.passenagers.remove(passenger)
                floors[passenger.origin].remove_passenger(passenger)
                passenger.origin = self.current_floor
                floors[self.current_floor].add_passenger(passenger)
                passenger.dropped()
                print("ELEVATOR {}: Dropped passenger {} on floor {}".format(self.id, passenger.id, self.current_floor))
                self.sleep(self.passenger_idle_time)

    def load_passengers(self, passengers, capacity):
        for passenger in passengers:
            if (capacity > 0):
                if (passenger.destination == self.current_floor):
                    continue
                self.add_passenger(passenger)
                self.sleep(self.passenger_idle_time)
                capacity -= 1
            else:
                break


    # Elevator lifecycle
    # 1. Open door (1000ms)
    # 2. Drop passengers
    ## 2.1. Check if passengers are on current floor
    ## 2.2. Remove passengers from elevator
    ## 2.3. Add passengers to floor
    # 3. Load passengers
    ## 3.1. Check if passengers are on current floor
    ## 3.2. Add passengers to elevator
    ## 3.3. Remove passengers from floor
    # 4. Close door (1000ms)
    # 5. Move to next floor
    # 6. Repeat from 1
    def execute_floor_move(self):
        self.open_door(self.door_delay)
        self.drop_passengers()
        checked_floor = floors[self.current_floor].check_floor()
        if (checked_floor.length > 0):
            remaining_capacity = self.capacity - len(self.passenagers)
            if (remaining_capacity > 0):
                self.load_passengers(checked_floor.passengers, remaining_capacity)
        self.close_door(self.door_delay)
        if (len(self.queue) > 0):
            self.execute_floor_move(self.queue.pop(0))
            self.sleep(self.speed)
            self.current_floor = self.current_floor + self.direction
        else:
            self.direction = 0
            self.available = True

    def call(self, floor):
        if (abs(floor) > abs(self.floors)):
            raise ValueError("Floor {} is out of bounds".format(floor))
        if (self.direction == 1 and floor > self.current_floor):
            self.queue(floor)
        elif (self.direction == -1 and floor < self.current_floor):
            self.queue(floor)
        elif (self.direction == 0):
            self.direction = 1 if floor > self.current_floor else -1
            self.queue(floor)
            self.execute_floor_move()

class Elevators(object):

    # delays (ms)
    door_delay = 1500
    caller_delay = 300
    floor_delay = 1000

    def __init__(self, count, floors, logic = ALGORITHIM):
        self.count = count
        self.floors = floors
        self.elevators = [Elevator(id(i), floors, 10, self.floor_delay, self.door_delay, self.caller_delay, 1) for i in range(count)]
        self.queued = set()
        self.waiting = set()
        if (logic == "random"):
            self.handle_call_logic = self.random_logic
        elif (logic == "fcfs"):
            self.handle_call_logic = self.fcfs_logic
        elif (logic == "sjf"):
            self.handle_call_logic = self.sjf_logic
        elif (logic == "srtf"):
            self.handle_call_logic = self.srtf_logic
        elif (logic == "edf"):
            self.handle_call_logic = self.edf_logic
        elif (logic == "llf"):
            self.handle_call_logic = self.llf_logic
        elif (logic == "rr"):
            self.handle_call_logic = self.rr_logic
        else:
            raise ValueError("Logic {} is not supported".format(logic))

        cprint(f'DECLARATION: Elevators created', 'magenta')

    def random_logic(self, floor):
        for elevator in self.elevators:
            if (elevator.available):
                elevator.call(floor)
                return elevator.id
            elif (elevator.direction == 1 and floor > elevator.current_floor):
                elevator.call(floor)
                return elevator.id
            elif (elevator.direction == -1 and floor < elevator.current_floor):
                elevator.call(floor)
                return elevator.id
            else:
                continue
        return False


    def call(self, origin, direction):
        if (origin < 1 or origin > self.floors):
            raise ValueError("Floor {} is out of bounds".format(origin))
        if (direction != 1 and direction != -1 and direction != 0):
            raise ValueError("Direction {} is not valid".format(direction))
        if (direction == 0):
            return

        self.waiting.add(origin)

    def simulate(self):
        while True:
            cprint("DEBUG | WAITING: {}".format(self.waiting), "yellow")
            cprint("DEBUG | QUEUED: {}".format(self.queued), "yellow")
            if (len(self.waiting) > 0):
                TERMINATE[1] = False
                floor = self.waiting.pop()
                if (floor in self.queued):
                    cprint("ELEVATORS: Floor {} is already queued".format(floor), "green")
                    continue
                handled = self.handle_call_logic(floor)
                if (handled):
                    self.queued.add(floor)
                    cprint("ELEVATORS: Found elevator {} for floor {}".format(handled, floor), "green")
                else:
                    cprint("ELEVATORS: No elevator available, adding floor {} to waiting list".format(floor), "green")
                    self.waiting.add(floor)
            else:
                if (all(TERMINATE)):
                    print("", flush=True)
                    break
                cprint("ELEVATORS: No waiting calls", "green")
                TERMINATE[1] = True
            time.sleep(1)

class Buliding(object):
    def __init__(self, floors, elevators, passengers):
        self.floors = [Floor(0, x) for x in range(0, floors)]
        self.elevators = Elevators(1, floors)
        self.passenger_count = passengers
        self.passengers = set()
        self.probabilities = Probability(PROBABILITY)

        cprint(f'DECLARATION: Building created', 'magenta')

    def new_passenger(self):
        trip = self.probabilities.rand_unique(2, default=1)
        passenger = Passenger(id(len(self.passengers)), trip[0], trip[1])

        self.passengers.add(passenger)
        cprint("BUILDING: New passenger {} from floor {} to floor {}".format(passenger.id, passenger.origin, passenger.destination), "blue")

        self.floors[passenger.origin].add_passenger(passenger)
        cprint("BUILDING: Passenger {} added to floor {}".format(passenger.id, passenger.origin), "blue")

        self.elevators.call(passenger.origin, passenger.destination - passenger.origin > 0 if 1 else -1)
        cprint("BUILDING: Elevator called to floor {}".format(passenger.origin), "blue")

        setTimeout(0.01, passenger.run)
        time.sleep(math.floor(random() * 2))

    def remove_passenger(self, passenger):
        self.passengers.remove(passenger)
        for floor in self.floors:
            if passenger in floor.passengers:
                floor.passengers.remove(passenger)
        cprint("BUILDING: Passenger {} removed from building".format(passenger.id), "blue")

    def simulate(self):
        for i in range(self.passenger_count):
            self.new_passenger()
        TERMINATE[0] = True

    async def run_dispatcher(self):
        setTimeout(0.01, self.elevators.simulate)
        setTimeout(0.01, self.simulate)
        while True:
            if (all(TERMINATE)):
                break
            await asyncio.sleep(1)
            if len(self.passengers) == 0:
                TERMINATE[0] = True
                break

    def run(self):
        LOOP.run_until_complete(self.run_dispatcher())
        LOOP.close()