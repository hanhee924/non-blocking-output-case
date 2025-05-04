import sys 
import time 
from io import StringIO
from subprocess import PIPE, Popen
from threading import Thread
from queue import Queue

lines = Queue()
cur_line = StringIO()
cur_output_last_time = time.time()
outputting = False

stop_flag = False 
read_output_thread = None
clock_thread = None

def read_output(process: Popen):
    global stop_flag, cur_line, cur_output_last_time, outputting
    outputting = True

    while not stop_flag:
        char = process.stdout.read(1)

        if not char or process.poll() is not None:
            return 
        
        cur_line.write(char)
        cur_output_last_time = time.time()

def clock():
    global cur_line, cur_output_last_time, outputting, stop_flag

    while not stop_flag:
        time.sleep(0.1)
        cur_line_interval = cur_line.getvalue()
        
        if time.time() - cur_output_last_time > 0.3 or cur_line_interval.find('\n') != -1:
            if len(cur_line.getvalue()) > 0:
                lines.put(cur_line.getvalue().rstrip('\n'))
                cur_line.seek(0)
                cur_line.truncate(0)
                outputting = False
        else:
            outputting = True

def start_observation(args):
    global read_output_thread
    global clock_thread

    process = Popen(
        args,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
        text=True,
        bufsize=0
    )

    read_output_thread = Thread(target=read_output, args=(process,))
    clock_thread = Thread(target=clock)

    read_output_thread.start()
    clock_thread.start()

    return process

def get():
    while outputting:
        time.sleep(0.01)
        
    return lines.get()

def write(process: Popen, data: str):
    while outputting:
        time.sleep(0.01)

    process.stdin.write(data)
    process.stdin.flush()

def exit(process: Popen):
    global stop_flag
    stop_flag = True
    process.terminate()
    process.wait()
    sys.exit(0)

# test
process =start_observation(["sample.exe"])
print(get())
write(process, "1\n")
print(get())
write(process, "1\n")
print(get())
exit(process)