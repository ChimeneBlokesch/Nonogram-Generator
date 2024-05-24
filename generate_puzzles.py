
import numpy as np
import random
import matplotlib.pyplot as plt
import os

np.random.seed(0)
random.seed(0)

FILLED_IN_COLOR = "#FF0000"


def generate_puzzle(width, height):
    # Generate a random puzzle grid
    grid = np.random.randint(0, 2, (height, width))
    row_amounts = [count_groups(row) for row in grid]
    col_amounts = [count_groups(col) for col in grid.T]
    return grid, row_amounts, col_amounts


def count_groups(arr):
    string = "".join([str(i) for i in arr])
    groups = string.split("0")
    return [len(group) for group in groups if group != ""]


def puzzle2image(grid, row_amounts, col_amounts, img_path, puzzle_name,
                 include_grid=False):
    # Convert a puzzle grid to an image

    row_amounts = prepend_amounts(row_amounts)
    col_amounts = prepend_amounts(col_amounts)

    height = len(grid)
    width = len(grid[0])

    cells = [["" for _ in range(width)] for _ in range(height)]
    cell_colours = None

    if include_grid:
        cell_colours = []

        for i in range(len(grid)):
            row = [FILLED_IN_COLOR if x == 1 else "#FFFFFF" for x in grid[i]]
            cell_colours.append(row)

    columns = ["\n\n".join(col) for col in col_amounts]
    rows = ["  " + "  ".join(row) + "  " for row in row_amounts]

    fig, axs = plt.subplots()
    axs.axis('tight')
    axs.axis('off')
    table = plt.table(cellText=cells, cellColours=cell_colours,
                      colLabels=columns, rowLabels=rows,
                      bbox=[0.0, 0.0, 1.0, 1.0])

    plt.tight_layout()
    plt.savefig(os.path.join(img_path, puzzle_name + '.png'))
    plt.close()


def prepend_amounts(amounts):
    new_arr = []
    max_len = max([len(line) for line in amounts])

    for line in amounts:
        new_line = [' '] * (max_len - len(line))
        new_line.extend([str(x) for x in line])
        new_arr.append(new_line)

    return new_arr


def lines_row_amounts(amounts, spaces: str):
    arr = prepend_amounts(amounts)
    new_arr = []

    for line in arr:
        new_arr.append(spaces.join(line))
    return [''.join(line) for line in new_arr]


def lines_col_amounts(amounts, prefix_spaces: int, spaces: str):
    arr = prepend_amounts(amounts)

    new_arr = []

    for i in range(len(arr[0])):
        new_line = [" " * prefix_spaces]
        new_line += [str(line[i]) for line in arr]
        new_arr.append(spaces.join(new_line))

    return '\n'.join([''.join(line) for line in new_arr])


def puzzle2text(grid, row_amount_lines, col_amount_strings, in_between_spaces=1,
                include_grid=False):
    # Convert a puzzle grid to a text
    # Make the row_amounts the same amount of elements in each column
    spaces = ' ' * in_between_spaces
    row_amount_lines = lines_row_amounts(row_amount_lines, spaces)
    col_amount_strings = lines_col_amounts(col_amount_strings,
                                           len(row_amount_lines[0]),
                                           spaces)

    text = ''
    text += col_amount_strings + '\n'

    for i, row in enumerate(grid):
        text += row_amount_lines[i]
        text += spaces

        if include_grid:
            text += spaces.join([str(cell) for cell in row])

        text += '\n'

    return text


def save_puzzle(grid, row_amounts, col_amounts, img_path, text_path, asp_path, puzzle_name, include_grid=False):
    os.makedirs(img_path, exist_ok=True)
    os.makedirs(text_path, exist_ok=True)
    os.makedirs(asp_path, exist_ok=True)

    # Save a puzzle to a file
    with open(os.path.join(text_path, puzzle_name + '.txt'), 'w') as f:
        f.write(puzzle2text(grid, row_amounts, col_amounts,
                in_between_spaces=2, include_grid=include_grid))

    with open(os.path.join(asp_path, puzzle_name + '.asp'), 'w') as f:
        f.write(puzzle2asp(grid, row_amounts, col_amounts,
                width, height, include_grid=include_grid))

    puzzle2image(grid, row_amounts, col_amounts, img_path,
                 puzzle_name, include_grid=include_grid)


def generate_puzzles(n, width, height, img_path, text_path, asp_path,
                     include_grid=False, prefix_name="puzzle_",
                     remove_value=0, amount_mistakes=0):
    """
    Generate n puzzles and save them to files

    Parameters
    ----------
    n : int
        Number of puzzles to generate
    width : int
        Width of the puzzle grid
    height : int
        Height of the puzzle grid
    img_path : str
        Path to save the images
    text_path : str
        Path to save the text files
    asp_path : str
        Path to save the ASP files
    include_grid : bool
        Whether to include the grid in the image
    prefix_name : str
        Prefix to add to the puzzle name
    remove_value : int
        Amount of filled cells to be set as not filled in the grid
    amount_mistakes : int
        Amount of unfilled cells to be set as filled in the grid
    """
    # Generate n puzzles
    for i in range(n):
        grid, row_amounts, col_amounts = generate_puzzle(width, height)
        puzzle_name = prefix_name + str(i)

        if include_grid and remove_value > 0:
            # Remove some filled cells from the grid
            filled_cells_indices = np.argwhere(grid == 1)
            random.shuffle(filled_cells_indices)
            for row, col in filled_cells_indices[:remove_value]:
                grid[row][col] = 0

        if include_grid and amount_mistakes > 0:
            # Replace some not-filled cells with filled cells, to create mistakes
            not_filled_cells_indices = np.argwhere(grid == 0)
            random.shuffle(not_filled_cells_indices)
            for row, col in not_filled_cells_indices[:amount_mistakes]:
                grid[row][col] = 1

        save_puzzle(grid, row_amounts, col_amounts, img_path,
                    text_path, asp_path, puzzle_name, include_grid=include_grid)


def puzzle2asp(grid, row_amounts, col_amounts, width, height,
               include_grid=False):
    strings = []

    strings.append(f"#const c = {width}. #const r = {height}.")

    strings.append("col_id(1..c). row_id(1..r).")

    strings.append("cell(RowId, ColId) :- row_id(RowId), col_id(ColId).")

    strings.append("{filled(RowId, ColId) : cell(RowId, ColId)}.")

    for row_id in range(len(row_amounts)):
        for i in range(len(row_amounts[row_id])):
            line = f"row_amount({row_id+1}, {i+1}, {row_amounts[row_id][i]})."
            strings.append(line)

    for col_id in range(len(col_amounts)):
        for i in range(len(col_amounts[col_id])):
            line = f"col_amount({col_id+1}, {i+1}, {col_amounts[col_id][i]})."
            strings.append(line)

    if include_grid:
        for i, row in enumerate(grid):
            for j, cell in enumerate(row):
                if cell != 1:
                    continue

                strings.append(f"filled({i+1}, {j+1}).")

    strings.append("""
sequence_row(R, 1, C, C) :- row_id(R), col_id(C), filled(R, C).
sequence_row(R, 2, C1, C1+1) :- row_id(R), col_id(C1), filled(R, C1), filled(R, C1+1).
sequence_row(R, L, C1, C2) :- row_id(R), col_id(C1), col_id(C2), C1 < C2, filled(R, C1), filled(R, C2), sequence_row(R, L - 1, C1, C2-1).

sequence_col(C, 1, R, R) :- col_id(C), row_id(R), filled(R, C).
sequence_col(C, 2, R1, R1+1) :- col_id(C), row_id(R1), filled(R1, C), filled(R1+1, C).
sequence_col(C, L, R1, R2) :- col_id(C), row_id(R1), row_id(R2), R1 < R2, filled(R1, C), filled(R2, C), sequence_col(C, L - 1, R1, R2-1).

group_row(R, 1, L, C1, C2) :- row_id(R), sequence_row(R, L, C1, C2),
                                not filled(R, C1-1), not filled(R, C2+1),
                                not sequence_row(R, _, C3, _) : col_id(C3), C3 < C1.

group_row(R, I, L, C3, C4) :- row_id(R), sequence_row(R, L, C3, C4), I > 1, col_id(C3), col_id(C4), % existence of group
                                not filled(R, C3-1), not filled(R, C4+1), % seperated group
                                group_row(R, I-1, _, _, C2), col_id(C2), C3 > C2, % previous group has a lower id
                                not group_row(R, I, _, C, _) : col_id(C), C3 != C. % no other group with the same id

group_col(C, 1, L, R1, R2) :- col_id(C), sequence_col(C, L, R1, R2),
                                not filled(R1-1, C), not filled(R2+1, C),
                                not sequence_col(C, _, R3, _) : row_id(R3), R3 < R1.

group_col(C, I, L, R3, R4) :- col_id(C), sequence_col(C, L, R3, R4), I > 1, row_id(R3), row_id(R4), % existence of group
                                not filled(R3-1, C), not filled(R4+1, C), % seperated group
                                group_col(C, I-1, _, _, R2), row_id(R2), R3 > R2, % previous group has a lower id
                                not group_col(C, I, _, R, _) : row_id(R), R3 != R. % no other group with the same id
""")

    strings.append("""
% All rows and columns have the correct amount of filled cells
:- not group_row(R, I, L, _, _), row_amount(R, I, L).
:- not group_col(C, I, L, _, _), col_amount(C, I, L).

:- group_row(R, I, L, _, _), not row_amount(R, I, L).
:- group_col(C, I, L, _, _), not col_amount(C, I, L).

#show filled/2.

""")

    return "\n".join(strings)


if __name__ == '__main__':
    n = 10
    width = 5
    height = 5
    generate_puzzles(n, width, height,
                     os.path.join("empty", "images"),
                     os.path.join("empty", "text"),
                     os.path.join("empty", "asp"),
                     include_grid=False)
    generate_puzzles(n, width, height,
                     os.path.join("fill-in", "images"),
                     os.path.join("fill-in", "text"),
                     os.path.join("fill-in", "asp"),
                     include_grid=True, remove_value=1)
    generate_puzzles(n, width, height,
                     os.path.join("validity", "invalid", "images"),
                     os.path.join("validity", "invalid", "text"),
                     os.path.join("validity", "invalid", "asp"),
                     include_grid=True, amount_mistakes=1)
    generate_puzzles(n, width, height,
                     os.path.join("validity", "valid", "images"),
                     os.path.join("validity", "valid", "text"),
                     os.path.join("validity", "valid", "asp"),
                     include_grid=True)
