# Elevator Simulator in Python
CLI-based elevator simulator written in Python to explore algorithms that minimizes wait time for all passengers and produce data for analysis.

## Installation
1. Clone the repository
2. Install Python 3.6 or higher
3. Install the requirements
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py -f [FLOORS] -e [ELEVATORS] -p [PASSENGERS] -a [ALGORITHM]
```
### Arguments
- `-f` or `--floors` - Number of floors in the building
- `-e` or `--elevators` - Number of elevators in the building
- `-p` or `--passengers` - Number of passengers in the building
- `-a` or `--algorithm` - Algorithm to use for elevator scheduling
- `-v` or `--verbose` - Verbose mode

### Commands
- `help` - Show help
- `exit` - Exit the program
- `run` - Run the simulation
- `reset` - Reset the simulation
- `set` - Set a variable

### Algorithms
- [ ] `fcfs` - First Come First Serve
- [ ] `lifo` - Last In First Out (Not implemented)
- [ ] `sjf` - Shortest Job First (Not implemented)
- [ ] `srtf` - Shortest Remaining Time First
- [ ] `rr` - Round Robin
- [ ] `edf` - Earliest Deadline First
- [ ] `llf` - Least Laxity First
- [x] `random` - Random

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
Please make sure to update tests as appropriate.

## Authors
- [**Omar Ibrahim**](github.com/omargfh)

## Acknowledgements
- [**Elevator Algorithm**](https://www.geeksforgeeks.org/elevator-scheduling-set-2-sjf-srtf/)

## Disclaimer
This project is for educational purposes only. It is not intended to be used in real life scenarios.

## TODO
- [ ] Implement Algorithms
- [ ] Fix asynchronous issues
- [ ] Use queues instead of sets

## Changelog
- 0.1.0
    - Initial release

## Meta
Omar Ibrahim – [@omaribb_](https://instagram.com/omaribb_) – [www.omar-ibrahim.com](https://www.omar-ibrahim.com)

Distributed under the MIT license. See ``LICENSE`` for more information.