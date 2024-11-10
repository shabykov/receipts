from typing import List


def valid(vals: List[str]) -> bool:
    vals = [val for val in vals if val != "."]
    if len(set(vals)) != len(vals):
        print(vals)

    return len(set(vals)) == len(vals)


def is_valid_cols(board: List[List[str]]) -> bool:
    for col in zip(*board):
        if not valid(col):
            return False



def is_valid_boxs(board: List[List[str]]) -> bool:
    for i in (0, 3, 6):
        for j in (0, 3, 6):
            if not valid([board[j + t][i + k] for t in range(3) for k in range(3)]):
                return False

    return True


if __name__ == "__main__":
    # board = [
    #     ["5", "3", ".", ".", "7", ".", ".", ".", "."]
    #     , ["6", ".", ".", "1", "9", "5", ".", ".", "."]
    #     , [".", "9", "8", ".", ".", ".", ".", "6", "."]
    #     , ["8", ".", ".", ".", "6", ".", ".", ".", "3"]
    #     , ["4", ".", ".", "8", ".", "3", ".", ".", "1"]
    #     , ["7", ".", ".", ".", "2", ".", ".", ".", "6"]
    #     , [".", "6", ".", ".", ".", ".", "2", "8", "."]
    #     , [".", ".", ".", "4", "1", "9", ".", ".", "5"]
    #     , [".", ".", ".", ".", "8", ".", ".", "7", "9"]
    # ]
    # print(is_valid_boxs(board))

    s = "race a car"
    s = s.replace(" ", "").replace(",", "").replace(".","").replace(":", "").lower()
    print(s[len(s)//2:], s[:len(s)//2])

    print(s[:len(s) // 2] == s[len(s) // 2 + 1:])


