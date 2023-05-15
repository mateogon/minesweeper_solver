import time

def time_function(func, repeats=1, *args, **kwargs):
    durations = []  # To store each execution's duration
    for _ in range(repeats):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        duration = end_time - start_time
        durations.append(duration)
    
    average_duration = sum(durations) / repeats
    total_duration = sum(durations)
    print(f"{func.__name__} took an average of {average_duration:.5f} seconds over {repeats} repeats.")
    print(f"Total time was {total_duration:.5f} seconds.")
    return result