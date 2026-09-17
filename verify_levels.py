# verify_levels.py
from levels import LEVELS, LEVEL_ORDER

UP, DOWN, LEFT, RIGHT = 1, 2, 3, 4
DIR_VEC = {
    UP:    (-1, 0),
    DOWN:  ( 1, 0),
    LEFT:  ( 0, -1),
    RIGHT: ( 0, 1),
}


def can_fly(grid, rows, cols, r, c):
    direction = grid[r][c]
    if direction == 0:
        return False
    dr, dc = DIR_VEC[direction]
    nr, nc = r + dr, c + dc
    while 0 <= nr < rows and 0 <= nc < cols:
        if grid[nr][nc] != 0:
            return False
        nr += dr
        nc += dc
    return True


def solve(grid):
    """BFS 搜索是否存在清空所有箭头的顺序。返回一条可行路径或 None。"""
    rows = len(grid)
    cols = len(grid[0])

    start = tuple(tuple(row) for row in grid)

    from collections import deque
    queue = deque()
    queue.append((start, []))
    visited = {start}

    while queue:
        state, path = queue.popleft()

        arrows = [(r, c) for r in range(rows) for c in range(cols) if state[r][c] != 0]
        if not arrows:
            return path

        for r, c in arrows:
            if can_fly(state, rows, cols, r, c):
                new_state = [list(row) for row in state]
                new_state[r][c] = 0
                new_state = tuple(tuple(row) for row in new_state)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((new_state, path + [(r, c)]))

    return None


if __name__ == "__main__":
    for key in LEVEL_ORDER:
        data = LEVELS[key]
        grid = data["grid"]
        path = solve(grid)
        print(f"{key} ({data['name']}):")
        if path is None:
            print("  ❌ 无解")
        else:
            print(f"  ✅ 有解，共 {len(path)} 步")
            print(f"  示例顺序: {path}")
        print()