import time

def tic():
    global start_time
    start_time = time.perf_counter()

def toc():
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.4f} seconds")
    return elapsed_time

# Example usage
tic()
# Code you want to time
time.sleep(2)  # Example code that takes time
toc()
