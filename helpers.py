import time
import threading

class SetTimeout:
    def __init__(self, timeout, callback):
        self.timeout = timeout
        self.callback = callback
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        time.sleep(self.timeout)
        self.callback()

    def cancel(self):
        self.thread.cancel()

def setTimeout(timeout, callback):
    return SetTimeout(timeout, callback)


def cprint(text, color):
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m',
    }
    print(colors[color] + f"{text : <70}" + colors['red'] + f"{timestamp() : >70}" + colors['reset'])
    with open("log.txt", "a") as f:
        f.write(f"{text}\n")

def timestamp():
    # h:m:s.ms
    return time.strftime("%H:%M:%S", time.localtime()) + f".{time.time() % 1 : .3f}"[1:]