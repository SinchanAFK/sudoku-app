from flask import Flask, render_template, request, jsonify
from solver import solve_with_steps, generate_puzzle, parse_txt
import copy, os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400
    content = file.read().decode('utf-8')
    puzzles = parse_txt(content)
    if not puzzles:
        return jsonify({'error': 'No valid puzzles found in file'}), 400
    return jsonify({'puzzles': puzzles, 'count': len(puzzles)})

@app.route('/solve', methods=['POST'])
def solve_route():
    data = request.json
    board = data.get('board')
    if not board:
        return jsonify({'error': 'No board provided'}), 400
    solution, steps = solve_with_steps(board)
    if solution is None:
        return jsonify({'error': 'Puzzle has no solution'}), 400
    return jsonify({'solution': solution, 'steps': steps, 'step_count': len(steps)})

@app.route('/generate', methods=['GET'])
def generate():
    difficulty = request.args.get('difficulty', 'medium')
    puzzle, solution = generate_puzzle(difficulty)
    return jsonify({'puzzle': puzzle, 'solution': solution})
@app.route('/compare', methods=['POST'])
def compare():
    import time
    import copy
    from solver import get_possible_values

    data = request.json
    board = data.get('board')

    if not board:
        return jsonify({'error': 'No board'}), 400

    def find_empty_simple(b):
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    return r, c
        return None

    def find_empty_mrv(b):
        best_cell = None
        best_values = None

        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    values = get_possible_values(b, r, c)
                    if best_values is None or len(values) < len(best_values):
                        best_cell = (r, c)
                        best_values = values

        return best_cell, best_values

    def count_constraints(b, r, c, num):
        count = 0

        for i in range(9):
            if b[r][i] == 0 and num in get_possible_values(b, r, i):
                count += 1
            if b[i][c] == 0 and num in get_possible_values(b, i, c):
                count += 1

        box_r = (r // 3) * 3
        box_c = (c // 3) * 3

        for i in range(box_r, box_r + 3):
            for j in range(box_c, box_c + 3):
                if b[i][j] == 0 and num in get_possible_values(b, i, j):
                    count += 1

        return count

    def solve_simple(b, counter):
        empty = find_empty_simple(b)
        if not empty:
            return True

        r, c = empty

        for num in get_possible_values(b, r, c):
            counter['calls'] += 1
            b[r][c] = num

            if solve_simple(b, counter):
                return True

            b[r][c] = 0

        return False

    def solve_mrv(b, counter):
        cell, values = find_empty_mrv(b)

        if not cell:
            return True

        r, c = cell

        for num in values:
            counter['calls'] += 1
            b[r][c] = num

            if solve_mrv(b, counter):
                return True

            b[r][c] = 0

        return False

    def solve_greedy_lcv(b, counter):
            cell = find_empty_simple(b)

            if not cell:
                return True

            r, c = cell
            values = get_possible_values(b, r, c)
            values = sorted(values, key=lambda num: count_constraints(b, r, c, num))

            for num in values:
                counter['calls'] += 1
                b[r][c] = num

                if solve_greedy_lcv(b, counter):
                    return True

                b[r][c] = 0

            return False

    def solve_branch_bound(b, counter):
        cell = find_empty_simple(b)

        if not cell:
            return True

        r, c = cell
        values = get_possible_values(b, r, c)

        if len(values) == 0:
            return False

        for num in values:
            counter['calls'] += 1
            b[r][c] = num

            failed = False
            for rr in range(9):
                for cc in range(9):
                    if b[rr][cc] == 0 and len(get_possible_values(b, rr, cc)) == 0:
                        failed = True
                        break
                if failed:
                    break

            if not failed and solve_branch_bound(b, counter):
                return True

            b[r][c] = 0

        return False

    def benchmark(name, solver_func, runs=1):
        total_time = 0
        total_calls = 0
        solved = False

        for _ in range(runs):
            test_board = copy.deepcopy(board)
            counter = {'calls': 0}

            start = time.perf_counter()
            solved = solver_func(test_board, counter)
            end = time.perf_counter()

            total_time += (end - start) * 1000
            total_calls += counter['calls']

        return {
            'name': name,
            'time': round(total_time / runs, 2),
            'calls': round(total_calls / runs),
            'solved': solved
        }
    results = [
        benchmark('MRV + Backtracking', solve_mrv),
        benchmark('Branch and Bound', solve_branch_bound),
        benchmark('Greedy (LCV) + Backtracking', solve_greedy_lcv),
        benchmark('Simple Backtracking', solve_simple)
    ]

    return jsonify({'algorithms': results})
if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)