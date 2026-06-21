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
    from solver import solve_with_steps
    import copy
    data = request.json
    board = data.get('board')
    if not board:
        return jsonify({'error': 'No board'}), 400
    def plain_solve(b, steps):
        for r in range(9):
            for c in range(9):
                if b[r][c] == 0:
                    from solver import get_possible_values
                    for num in get_possible_values(b, r, c):
                        b[r][c] = num
                        steps.append(1)
                        if plain_solve(b, steps):
                            return True
                        b[r][c] = 0
                    return False
        return True

    plain_steps = []
    plain_board = copy.deepcopy(board)
    plain_solve(plain_board, plain_steps)
    return jsonify({'plain_steps': len(plain_steps)})
if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    app.run(debug=True)