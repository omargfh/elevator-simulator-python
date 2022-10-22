from elevator import *
import argparse
def run():
    # Create a Building instance
    building = Buliding(FLOORS, ELEVATORS, PEOPLE)
    # Expose floors
    floors = building.floors
    # Run the simulation
    building.run()

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
    ALGORITHM = args.algorithm
    VERBOSE = args.verbose

    while True:
        cmd = input("> ")
        if cmd == "run":
            print(f"Running simulation with {FLOORS} floors, {ELEVATORS} elevators, and {PEOPLE} people...")
            run()
        elif cmd == "exit":
            break
        elif cmd.startswith("-f"):
            FLOORS = int(cmd.split(" ")[1])
            print(f"Set number of floors to {FLOORS}")
        elif cmd.startswith("-e"):
            ELEVATORS = int(cmd.split(" ")[1])
            print(f"Set number of elevators to {ELEVATORS}")
        elif cmd.startswith("-p"):
            PEOPLE = int(cmd.split(" ")[1])
            print(f"Set number of people to {PEOPLE}")
        elif cmd.startswith("-a"):
            ALGORITHM = cmd.split(" ")[1]
            print(f"Set algorithm to {ALGORITHM}")
        elif cmd == "-v":
            VERBOSE = not VERBOSE
            print(f"Set verbose to {VERBOSE}")
        elif cmd == "help":
            print("Commands:")
            print("run: run the simulation")
            print("exit: exit the program")
            print("-f [FLOORS]: change the number of floors")
            print("-e [ELEVATORS]: change the number of elevators")
            print("-p [PEOPLE]: change the number of people")
            print("-a [ALGORITHM]: change the scheduling algorithm")
            print("-v: toggle verbose output")
            print("help: print this help message")
        else:
            print("Invalid command")


if __name__ == "__main__":
    main()