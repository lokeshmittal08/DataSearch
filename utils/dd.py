
import sys
import inspect
import time 

def dd(*args):
    # Get the current stack frame
    current_frame = inspect.currentframe()
    file_name = ""
    if current_frame is not None:
        # Get the frame of the caller
        caller_frame = current_frame.f_back
        if caller_frame is not None:
            # Get the file name and line number of the caller
            file_name = caller_frame.f_code.co_filename
            line_number = caller_frame.f_lineno
    print(f"Logged from file: {file_name}, line number: {line_number}")
    for arg in args:
        print(arg)
    sys.exit()
    