import multiprocessing
import logging
from functools import partial

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def place_queens(row, n, cols, diag1, diag2, board, solutions):
    if row == n:
        solutions.append(board[:])
        logging.info(f"Solution found! Total solutions: {len(solutions)}")
        return

    for col in range(n):
        if not (cols & (1 << col) or diag1 & (1 << (row - col + n - 1)) or diag2 & (1 << (row + col))):
            board[row] = col
            place_queens(row + 1, n,
                         cols | (1 << col),
                         diag1 | (1 << (row - col + n - 1)),
                         diag2 | (1 << (row + col)),
                         board,
                         solutions)


# Worker task that starts placing queens from a specific first-row placement
def worker_task(n, col):
    logging.info(f"Worker started solving for first queen at column {col}")
    solutions = []
    # Place the queen in the first row at column `col`
    cols = 1 << col
    diag1 = 1 << (0 - col + n - 1)
    diag2 = 1 << (0 + col)
    board = [-1] * n
    board[0] = col

    # Solve the rest of the board starting from the second row
    place_queens(1, n, cols, diag1, diag2, board, solutions)

    logging.info(f"Worker finished for column {col} with {len(solutions)} solutions found.")
    return solutions


def solve_n_queens_parallel_main(n):
    logging.info(f"Starting to solve {n}-queens puzzle.")

    # Use multiprocessing to handle the initial placements
    with multiprocessing.Pool(multiprocessing.cpu_count()) as pool:
        results = pool.map(partial(worker_task, n), range(n))

    # Combine the results from all processes
    all_solutions = [solution for result in results for solution in result]

    logging.info(f"Completed solving {n}-queens puzzle. Total solutions: {len(all_solutions)}")

    return all_solutions

if __name__ == "__main__":
    n = 8
    solutions = solve_n_queens_parallel_main(n)
    print(f"Number of solutions for {n}-queens puzzle: {len(solutions)}")

    # Optionally print one solution if available
    if solutions:
        print(f"One solution for {n}-queens puzzle:")
        print(solutions[0])
