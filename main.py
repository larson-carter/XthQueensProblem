import multiprocessing
import logging
from functools import partial
import time

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


def place_queens_bitwise(n, row=0, cols=0, diag1=0, diag2=0):
    if row == n:
        return 1
    count = 0
    available = ((1 << n) - 1) & ~(cols | diag1 | diag2)
    while available:
        pos = available & -available
        available ^= pos
        count += place_queens_bitwise(n, row + 1,
                                      cols | pos,
                                      (diag1 | pos) << 1,
                                      (diag2 | pos) >> 1)
    return count


def worker_task(n, col, progress_queue):
    logging.info(f"Worker started solving for first queen at column {col}")
    cols = 1 << col
    diag1 = 1 << (0 - col + n - 1)
    diag2 = 1 << (0 + col)
    solutions = place_queens_bitwise(n, 1, cols, diag1 << 1, diag2 >> 1)
    progress_queue.put(1)
    logging.info(f"Worker finished for column {col} with {solutions} solutions found.")
    return solutions


def progress_monitor(n, progress_queue):
    work_done = 0
    start_time = time.time()
    while work_done < n:
        work_done += progress_queue.get()
        progress = (work_done / n) * 100
        elapsed_time = time.time() - start_time
        estimated_total_time = elapsed_time * (n / work_done)
        remaining_time = estimated_total_time - elapsed_time
        logging.info(f"Progress: {progress:.2f}% | Elapsed: {elapsed_time:.2f}s | ETA: {remaining_time:.2f}s")


def solve_n_queens_parallel_main(n):
    logging.info(f"Starting to solve {n}-queens puzzle.")

    manager = multiprocessing.Manager()
    progress_queue = manager.Queue()

    monitor_process = multiprocessing.Process(target=progress_monitor, args=(n, progress_queue))
    monitor_process.start()

    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        results = pool.map(partial(worker_task, n, progress_queue=progress_queue), range(n))

    total_solutions = sum(results)

    monitor_process.join()

    logging.info(f"Completed solving {n}-queens puzzle. Total solutions: {total_solutions}")
    return total_solutions


if __name__ == "__main__":
    n = 24
    solutions = solve_n_queens_parallel_main(n)
    print(f"Number of solutions for {n}-queens puzzle: {solutions}")