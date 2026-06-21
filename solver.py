def is_valid(board, row, col, num):
    if num in board[row]:
        return False
    if num in [board[r][col] for r in range(9)]:
        return False
    box_r, box_c = 3 * (row // 3), 3 * (col // 3)
    for r in range(box_r, box_r + 3):
        for c in range(box_c, box_c + 3):
            if board[r][c] == num:
                return False
    return True

def get_possible_values(board, row, col):
    return [n for n in range(1, 10) if is_valid(board, row, col, n)]

def find_empty_mrv(board):
    min_options = 10
    best_cell = None
    for r in range(9):
        for c in range(9):
            if board[r][c] == 0:
                options = len(get_possible_values(board, r, c))
                if options < min_options:
                    min_options = options
                    best_cell = (r, c)
    return best_cell

def solve(board):
    cell = find_empty_mrv(board)
    if not cell:
        return True
    row, col = cell
    for num in get_possible_values(board, row, col):
        board[row][col] = num
        if solve(board):
            return True
        board[row][col] = 0
    return False

def solve_with_steps(board):
    steps = []
    def backtrack(b):
        cell = find_empty_mrv(b)
        if not cell:
            return True
        row, col = cell
        for num in get_possible_values(b, row, col):
            b[row][col] = num
            steps.append({"row": row, "col": col, "val": num, "action": "place"})
            if backtrack(b):
                return True
            b[row][col] = 0
            steps.append({"row": row, "col": col, "val": 0, "action": "backtrack"})
        return False
    import copy
    board_copy = copy.deepcopy(board)
    solved = backtrack(board_copy)
    return (board_copy if solved else None), steps

def generate_puzzle(difficulty="medium"):
    import random, copy
    board = [[0]*9 for _ in range(9)]
    for box in range(0, 9, 3):
        nums = list(range(1, 10))
        random.shuffle(nums)
        for r in range(3):
            for c in range(3):
                board[box+r][box+c] = nums.pop()
    solve(board)
    solution = copy.deepcopy(board)
    clues = {"easy": 36, "medium": 28, "hard": 22}
    cells_to_remove = 81 - clues.get(difficulty, 28)
    positions = list(range(81))
    random.shuffle(positions)
    for pos in positions[:cells_to_remove]:
        board[pos//9][pos%9] = 0
    return board, solution

def parse_txt(content):
    puzzles = []
    current = []
    for line in content.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            if len(current) == 9:
                puzzles.append(current)
            current = []
            continue
        row = [int(ch) if ch.isdigit() else 0 for ch in line if ch.isdigit() or ch in '._-']
        if len(row) == 9:
            current.append(row)
    if len(current) == 9:
        puzzles.append(current)
    return puzzles