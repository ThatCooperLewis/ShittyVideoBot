import traceback

# Hardcode debug state for verbose logging
debug_bool = True

# Yeah, I know there are better ways. This was easy!
def debug(log_str):
    if debug_bool: print("[DEBUG]: " + log_str) 

def debug_crash():
    if debug_bool: traceback.print_exc()