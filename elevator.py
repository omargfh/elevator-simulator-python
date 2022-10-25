from random import random
from tabnanny import check
import time
import math
import asyncio
from helpers import setTimeout, cprint, timestamp
from constants import *

TERMINATE = [False, False, False]
floors = []
probability = None
building = None
elevators = None

class VirtualTime():
    def __init__(self):
        self.time = 0

    def increment(self, amount):
        self.time += amount

    def get(self):
        return self.time

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
        for p in self.probabilites:
            cprint(f"Probability: {p.probability} Value: {p.value}", 'cyan')


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

class Passenger(object):
    def __init__(self, id, start, end, random=random):
        self.id = id
        self.origin = start
        self.destination = end
        self.wait = []

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

        cprint(f'DECLARATION: Passenger {self.id} created', 'magenta')


    def gen_passengers(self, count, start, end):
        return [Passenger(i, start.rand(), end.rand()) for i in range(count)]

    def dropped(self):
        if self.origin == self.destination and self.origin == STAR_FLOOR:
            building.remove_passenger(self)
        return True

    def move(self):
        self.destination = list(filter(lambda x: x != self.origin, probability.rand_unique(2, default=self.origin)))[0]
        print(f'Passenger {self.id} decided to go from {self.origin} to {self.destination}')

    def run(self):
        direction = 1 if self.origin < self.destination else (-1 if self.origin > self.destination else 0)
        if (direction == 1 and not floors[self.origin].called_up):
            floors[self.origin].call_up()
        elif (direction == -1 and not floors[self.origin].called_down):
            floors[self.origin].call_down()

        while self.origin != self.destination:
            continue
        time_to_move = self.random()
        setTimeout(time_to_move, self.move)

class Floor(object):
    def __init__(self, passengers_count, floor):
        self.passengers_count = passengers_count
        self.passengers = set()
        self.floor = floor
        self.called_up = False
        self.called_down = False

        cprint(f'DECLARATION: Floor {self.floor} created', 'magenta')

    def add_passenger(self, passenger):
        self.passengers.add(passenger)

    def remove_passenger(self, passenger):
        passenger in self.passengers and self.passengers.remove(passenger)

    def call_up(self):
        self.called_up = True
        print(f'Floor {self.floor} called up')

    def call_down(self):
        self.called_down = True
        print(f'Floor {self.floor} called down')

    def uncall(self):
        self.called_up = False
        self.called_down = False

    def print_summary(self):
        print(f'Floor {self.floor} has {len(self.passengers)} passengers and floor is called up: {self.called_up} and called down: {self.called_down}')

    def check_floor(self):
        available_passengers = [x for x in self.passengers if x.origin == self.floor and x.destination != self.floor]
        return {
            "len": len(available_passengers),
            "passengers": available_passengers
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
        self.queue = []
        self.door_delay = door_delay
        self.passenger_idle_time = passenger_idle_time
        self.time = 0

        cprint(f'DECLARATION: Elevator {self.id} created', 'magenta')

    def add_to_queue(self, floor):
        if floor not in self.queue:
            self.queue.append(floor)

    def add_passenger(self, passenger):
        if passenger.destination == passenger.origin:
            return
        elif (self.capacity - len(self.passenagers)) > 0:
            self.passenagers.add(passenger)
            floors[passenger.origin].remove_passenger(passenger)
            self.add_to_queue(passenger.destination)

    def sleep(self, time):
        self.time += time

    def open_door(self, sleep_time = 1000):
        print("ELEVATOR {}: Opening door on floor {}".format(self.id, self.current_floor))
        self.sleep(sleep_time)

    def close_door(self, sleep_time = 1000):
        print("ELEVATOR {}: Closing door on floor {}".format(self.id, self.current_floor))
        self.sleep(sleep_time)

    def drop_passengers(self):
        lock_psg = self.passenagers.copy()
        for passenger in lock_psg:
            if passenger.destination == self.current_floor:
                self.passenagers.remove(passenger)
                floors[passenger.origin].remove_passenger(passenger)
                passenger.origin = self.current_floor
                floors[self.current_floor].add_passenger(passenger)
                passenger.dropped()
                print("ELEVATOR {}: Dropped passenger {} on floor {}".format(self.id, passenger.id, self.current_floor))
                self.sleep(self.passenger_idle_time)

    def load_passengers(self, passengers, capacity):
        length = 0
        while True:
            if (len(passengers) == 0):
                break
            if (self.capacity - len(self.passenagers)) == 0:
                break
            passenger = passengers.pop()
            if passenger.origin == self.current_floor:
                length += 1
                self.passenagers.add(passenger)
                floors[passenger.origin].remove_passenger(passenger)
                self.add_to_queue(passenger.destination)
                print("ELEVATOR ROUTINE {}: Loaded passenger {} on floor {}".format(self.id, passenger.id, self.current_floor))
        return length

    def dequeue_current_floor(self):
        if self.current_floor in self.queue:
            self.queue.remove(self.current_floor)

    def next_floor(self):
        if len(self.queue) == 0:
            return None
        if self.direction == 1:
            return min(self.queue)
        elif self.direction == -1:
            return max(self.queue)
        else:
            return None

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
        # Debug Information
        cprint(f'DEBUG INFO: Elevator {self.id} has queue {self.queue}', 'yellow')
        cprint(f'DEBUG INFO: Elevator {self.id} has {len(self.passenagers)} passengers', 'yellow')
        cprint(f'DEBUG INFO: Elevator {self.id} has current floor {self.current_floor}', 'yellow')
        cprint(f'DEBUG INFO: Elevator {self.id} has direction {self.direction}', 'yellow')
        cprint(f'DEBUG INFO: Elevator {self.id} has available {self.available}', 'yellow')

        # Open door
        self.open_door(self.door_delay)
        cprint(f'ELEVATOR {self.id}: Door opened on floor {self.current_floor}', 'red')

        # Drop passengers
        dropped_count = sum([1 for passenger in self.passenagers if passenger.destination == self.current_floor])
        self.drop_passengers()
        cprint(f'ELEVATOR {self.id}: Dropped {dropped_count} passengers on floor {self.current_floor}', 'red')

        # Load passengers
        checked_floor = floors[self.current_floor].check_floor()
        if (checked_floor['len'] > 0):
            remaining_capacity = self.capacity - len(self.passenagers)
            if (remaining_capacity > 0):

                cprint(f'ELEVATOR {self.id}: Found {checked_floor["len"]} passengers on floor {self.current_floor}', 'red')
                loaded = self.load_passengers(checked_floor['passengers'], remaining_capacity)

                remaining_capacity = self.capacity - min(remaining_capacity, len(self.passenagers))                          # this might fail if integrity is violated
                if (not remaining_capacity == (self.capacity - len(self.passenagers))):
                    cprint(f'DEBUG IN ELEVATOR {self.id}: Integrity check violated on floor {self.current_floor}', 'yellow')

                # log information
                cprint(f'ELEVATOR {self.id}: Loaded {loaded} passengers on floor {self.current_floor}', 'red')
                cprint(f'ELEVATOR {self.id}: Remaining capacity {remaining_capacity} on floor {self.current_floor}', 'red')

        # Close door
        self.close_door(self.door_delay)
        cprint(f'ELEVATOR {self.id}: Door closed on floor {self.current_floor}', 'red')

        # Dequeue current floor
        self.dequeue_current_floor()

        # Move to next floor
        if (len(self.queue) > 0):
            self.sleep(self.speed)
            self.current_floor = self.next_floor()
            self.execute_floor_move()
            cprint(f'ELEVATOR {self.id}: Moving to floor {self.current_floor}', 'red')
        else:
            self.direction = 0
            self.available = True
            cprint(f'ELEVATOR {self.id}: Elevator is now idle', 'red')

    def call(self, floor, force=False):
        force and self.add_to_queue(floor)
        if (abs(floor) > abs(self.floors)):
            raise ValueError("Floor {} is out of bounds".format(floor))
        if (self.direction == 1 and floor > self.current_floor):
            self.add_to_queue(floor)
        elif (self.direction == -1 and floor < self.current_floor):
            self.add_to_queue(floor)
        elif (self.direction == 0):
            self.direction = 1 if floor > self.current_floor else -1
            self.add_to_queue(floor)
            self.execute_floor_move()

    def run(self):
        while True:
            if (self.available and len(self.queue) > 0):
                self.available = False
                self.execute_floor_move()
            else:
                self.sleep(0.5)

class Elevators(object):

    # delays (ms)
    door_delay = 1500
    caller_delay = 300
    floor_delay = 1000

    def __init__(self, count, floors, logic = ALGORITHIM):
        self.count = count
        self.floors = floors
        self.elevators = [Elevator(id(i), floors, 100, self.floor_delay, self.door_delay, self.caller_delay, 1) for i in range(count)]
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
                elevator.call(floor, force=True)
                return elevator.id
            elif (elevator.direction == 1 and floor > elevator.current_floor):
                elevator.call(floor, force=True)
                return elevator.id
            elif (elevator.direction == -1 and floor < elevator.current_floor):
                elevator.call(floor, force=True)
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
            for floor in floors:
                called = floor.called_up or floor.called_down
                floor.uncall()
                floor = floor.floor
                if ((not floor in self.waiting) and called):
                    self.waiting.add(floor)
                    self.handle_call_logic(floor)
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

        direction = passenger.destination - passenger.origin > 0 if 1 else -1
        should_call = False
        if (self.floors[passenger.origin].called_up == False and direction == 1):
            self.floors[passenger.origin].called_up = True
            should_call = True
        elif (self.floors[passenger.origin].called_down == False and direction == -1):
            self.floors[passenger.origin].called_down = True
            should_call = True
        should_call and self.elevators.call(passenger.origin, direction)
        should_call and cprint("BUILDING: Elevator called to floor {}".format(passenger.origin), "blue")

        setTimeout(0.01, passenger.run)
        time.sleep(math.floor(random() * 2))

    def remove_passenger(self, passenger):
        not passenger in self.passengers and cprint("BUILDING: Passenger {} is not in building".format(passenger.id), "red")
        passenger in self.passengers and self.passengers.remove(passenger)
        for floor in self.floors:
            if passenger in floor.passengers:
                floor.passengers.remove(passenger)
        cprint("BUILDING: Passenger {} removed from building".format(passenger.id), "blue")

    def simulate(self):
        for i in range(self.passenger_count):
            self.new_passenger()
        # print summary of each floor
        for floor in self.floors:
            floor.print_summary()
        TERMINATE[0] = True

    async def run_dispatcher(self):
        setTimeout(0.01, self.elevators.simulate)
        setTimeout(0.01, self.simulate)
        for elevator in self.elevators.elevators:
            setTimeout(0.01, elevator.run)
        while True:
            # check if all passengers are done
            if (all(TERMINATE)):
                break
            await asyncio.sleep(1)
            if len(self.passengers) == 0:
                TERMINATE[0] = True
                break

    def run(self):
        LOOP.run_until_complete(self.run_dispatcher())
        LOOP.close()

def run():
    cprint(f'---- ELEVATOR SIMULATOR ----', 'cyan');
    # Create a Building instance
    global building
    building = Buliding(FLOORS, ELEVATORS, PEOPLE)
    # Expose floors
    global floors
    floors = building.floors
    # expose elevators
    global elevators
    elevators = building.elevators
    # Expose probability
    global probability
    probability = Probability(PROBABILITY)
    # Run the simulation
    building.run()