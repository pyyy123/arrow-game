"""
路径检测逻辑测试（不依赖 Pygame）
运行：python tests/test_logic.py
"""

# 方向定义（与 main.py 保持一致）
UP, DOWN, LEFT, RIGHT, EMPTY = 1, 2, 3, 4, 0
DIR_VEC = {
    UP:    (-1, 0),
    DOWN:  ( 1, 0),
    LEFT:  ( 0, -1),
    RIGHT: ( 0, 1),
}


def is_blocked(grid, row, col, rows, cols):
    """路径上是否有箭头。0=空，1-4=箭头方向。"""
    direction = grid[row][col]
    if direction == 0:
        return True

    dr, dc = DIR_VEC[direction]
    r, c = row + dr, col + dc
    while 0 <= r < rows and 0 <= c < cols:
        if grid[r][c] != 0:
            return True
        r += dr
        c += dc
    return False


# ---------- 测试用例 ----------

def test_T01_no_block():
    grid = [
        [RIGHT, 0, 0],
        [0, 0, 0],
    ]
    assert is_blocked(grid, 0, 0, 2, 3) is False
    print("T01 通过：前方无阻挡可飞出")


def test_T02_blocked():
    grid = [
        [RIGHT, 0, UP],
        [0, 0, 0],
    ]
    assert is_blocked(grid, 0, 0, 2, 3) is True
    print("T02 通过：前方有阻挡不可飞出")


def test_T03_edge():
    grid = [
        [0, 0, RIGHT],
    ]
    assert is_blocked(grid, 0, 2, 1, 3) is False
    print("T03 通过：边缘箭头正常飞出")


def test_T04_four_directions():
    for d in [UP, DOWN, LEFT, RIGHT]:
        grid = [[0] * 5 for _ in range(5)]
        grid[2][2] = d
        assert is_blocked(grid, 2, 2, 5, 5) is False
    print("T04 通过：四方向检测正常")


def test_left_edge_arrow_left_out_of_bounds():
    grid = [
        [3, 0],
        [0, 0],
    ]
    assert is_blocked(grid, 0, 0, 2, 2) is False
    print("T05 通过：左边缘朝左越界判断正确")


def test_T06_back_to_back():
    grid = [
        [LEFT, 0, RIGHT],
    ]
    assert is_blocked(grid, 0, 0, 1, 3) is False
    assert is_blocked(grid, 0, 2, 1, 3) is False
    print("T06 通过：背对背不阻挡")


def test_T07_empty_cell():
    grid = [[0, 0], [0, 0]]
    assert is_blocked(grid, 0, 0, 2, 2) is True
    print("T07 通过：空格不可点")


def test_T08_same_line_multiple():
    grid = [
        [RIGHT, 0, UP, 0, DOWN],
    ]
    assert is_blocked(grid, 0, 0, 1, 5) is True
    print("T08 通过：同一行多个箭头，最近阻挡生效")

def test_T09_top_boundary_up():
    grid = [
        [UP, 0],
        [0, 0],
    ]

    # (0,0) 位置的箭头朝上
    # 上方已经越界，不应该访问 grid[-1]
    assert is_blocked(grid, 0, 0, 2, 2) is False

    print("T09 通过：顶部朝上不会数组越界")


if __name__ == "__main__":
    test_T01_no_block()
    test_T02_blocked()
    test_T03_edge()
    test_T04_four_directions()
    test_left_edge_arrow_left_out_of_bounds()
    test_T06_back_to_back()
    test_T07_empty_cell()
    test_T08_same_line_multiple()
    test_T09_top_boundary_up()

    print("\n全部测试通过 ✓")