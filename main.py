from elevator import *
import argparse

algos = ['fcfs', 'sjf', 'srtf', 'random', 'llf', 'edf', 'lifo']
def main():
    # usage: python main.py -f [FLOORS] -e [ELEVATORS] -p [PEOPLE] -a [ALGORITHM] -v
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--floors", type=int, default=5, help="Number of floors")
    parser.add_argument("-e", "--elevators", type=int, default=1, help="Number of elevators")
    parser.add_argument("-p", "--people", type=int, default=10, help="Number of people")
    parser.add_argument("-a", "--algorithm", type=str, default="random", help="Scheduling algorithm")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    # Set global variables
    global FLOORS
    global ELEVATORS
    global PEOPLE
    global ALGORITHM
    global VERBOSE
    FLOORS = args.floors
    ELEVATORS = args.elevators
    PEOPLE = args.people
    ALGORITHM = args.algorithm in algos and args.algorithm or "random"
    VERBOSE = args.verbose

    while True:
        cmd = input("> ")
        if cmd == "run":
            print("Running simulation...")
            print("Floors: {}, Elevators: {}, People: {}, Algorithm: {}".format(FLOORS, ELEVATORS, PEOPLE, ALGORITHM))
            run()
        elif cmd == "exit":
            break
        elif cmd.startswith("set -f"):
            FLOORS = int(cmd.split(" ")[1])
            print(f"Set number of floors to {FLOORS}")
        elif cmd.startswith("set -e"):
            ELEVATORS = int(cmd.split(" ")[1])
            print(f"Set number of elevators to {ELEVATORS}")
        elif cmd.startswith("set -p"):
            PEOPLE = int(cmd.split(" ")[1])
            print(f"Set number of people to {PEOPLE}")
        elif cmd.startswith("set -a"):
            if cmd.split(" ")[1] in algos:
                ALGORITHM = cmd.split(" ")[1]
                print(f"Set algorithm to {ALGORITHM}")
            else:
                print(f"Invalid algorithm. Valid algorithms: {algos}")
        elif cmd == "set -v":
            VERBOSE = not VERBOSE
            print(f"Set verbose to {VERBOSE}")
        elif cmd == "reset":
            FLOORS = 5
            ELEVATORS = 1
            PEOPLE = 10
            ALGORITHM = "random"
            VERBOSE = False
            print("Reset all variables")

        elif cmd == "inputs":
            print("Floors: {}".format(FLOORS))
            print("Elevators: {}".format(ELEVATORS))
            print("People: {}".format(PEOPLE))
            print("Algorithm: {}".format(ALGORITHM))
        elif cmd == "help":
            print("Commands:")
            print("run: run the simulation")
            print("inputs: print the current inputs")
            print("reset: reset the inputs to default")
            print("set -f [FLOORS]: change the number of floors")
            print("set -e [ELEVATORS]: change the number of elevators")
            print("set -p [PEOPLE]: change the number of people")
            print("set -a [ALGORITHM]: change the scheduling algorithm")
            print("set -v: toggle verbose output")
            print("help: print this help message")
            print("exit: exit the program")
        else:
            print("Invalid command")


if __name__ == "__main__":
    main()