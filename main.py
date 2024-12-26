from colorama import Fore, Style


import time

timer_start_time = None


def start_timer():
    global timer_start_time
    timer_start_time = time.perf_counter()


def stop_timer():
    global timer_start_time
    if timer_start_time is None:
        print("Cronometrul nu a fost pornit!")
        return None
    elapsed_time = (time.perf_counter() - timer_start_time)   # `Secunde`
    timer_start_time = None          # Reserare
    return elapsed_time


def print_board(board: list[list[str]]):  # board is an N x N char matrix.
    print("\n---------- Tabla de joc actuala: ----------\n")
    for i in board:
        print("| ", end="")
        for j in i:
            if j == 'X':
                print(Fore.RED + "X" + Style.RESET_ALL, end="")
            elif j == 'O':
                print(Fore.GREEN + "O" + Style.RESET_ALL, end="")
            else:
                print(" ", end="")
            print(" | ", end="")
        print("\n", end="")
    print()


# functia de evaluare a pozitiei curente. Returneaza +-10 daca castiga AI-ul/Jucatorul.
# In caz ca nu a castigat nimeni returneaza 0
def evaluate_current_board(board: list[list[str]], ai_char: str, player_char: str, win_length:int) -> int:
    n = len(board)  # Dimensiunea tablei

    # Verificare pe linii
    for linie in range(n):
        for start in range(n - win_length + 1):
            if all(board[linie][start + k] == ai_char for k in range(win_length)):
                return 100
            if all(board[linie][start + k] == player_char for k in range(win_length)):
                return -100

    # Verificare pe coloane
    for coloana in range(n):
        for start in range(n - win_length + 1):
            if all(board[start + k][coloana] == ai_char for k in range(win_length)):
                return 100
            if all(board[start + k][coloana] == player_char for k in range(win_length)):
                return -100

    # Verificare pe diagonale principale
    for linie in range(n - win_length + 1):
        for coloana in range(n - win_length + 1):
            if all(board[linie + k][coloana + k] == ai_char for k in range(win_length)):
                return 100
            if all(board[linie + k][coloana + k] == player_char for k in range(win_length)):
                return -100

    # Verificare pe diagonale secundare
    for linie in range(n - win_length + 1):
        for coloana in range(win_length - 1, n):
            if all(board[linie + k][coloana - k] == ai_char for k in range(win_length)):
                return 100
            if all(board[linie + k][coloana - k] == player_char for k in range(win_length)):
                return -100
    return 0


# functie care returneaza nr de spatii ramase pe tabla de joc
def number_of_left_moves(board: list[list[str]]):
    left_spaces = 0
    for line in board:
        for elem in line:
            if elem == " ":
                left_spaces += 1
    return left_spaces


# functie care genereaza toate murarile posibile ale urmatorului jucator (om/AI)
# daca gaseste o pozitie libera o populeaza cu simbolul jucatorului respectiv si genereaza o tabla noua
def compute_posible_boards(board: list[list[str]], next_char: str) -> list[list[list[str]]]:
    list_of_boards = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == " ":
                new_board = []
                for a in range(len(board)):
                    line = []
                    for b in range(len(board[0])):
                        line.append(board[a][b])
                    new_board.append(line)
                new_board[i][j] = next_char
                list_of_boards.append(new_board)
    return list_of_boards


# functie recursiva care foloseste algoritmul minimax FARA retezare alfa beta (adica varianta clasica)
# returneaza cea mai buna mutare in functie de adancimea arborelui care a fost setata
def compute_next_move(boardd: list[list[str]], ai_char: str, player_char: str, depth: int, max_depth: int, win_length:int) -> tuple[int, list[list[str]]]:
    results = []
    # evaluarea tablei curente
    move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char, win_length=win_length)
    # daca pe tabla exista un castigator cineva inchei jocul
    if move_score == 100 or move_score == -100:
        return (move_score - depth) if move_score == 100 else (move_score + depth), boardd
    # daca am ajuns la adancimea maxima de cautare ma opresc
    if depth == max_depth:
        move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char, win_length=win_length)
        return move_score - depth, boardd
    else:
        if depth % 2 == 0:  # daca sunt la un nivel maximizant
            if number_of_left_moves(board=boardd) > 0:
                possible_moves = compute_posible_boards(board=boardd, next_char=ai_char)
                for pm in possible_moves:
                    # generez tot subarborele
                    results.append(compute_next_move(pm, ai_char, player_char, depth + 1, max_depth,win_length))
                # selectez cel mai avatajos scenariu
                max_result = max(results, key=lambda x: x[0])
                if depth == 0:
                    #daca sunt pe primul nivel de arbore intorc tabla urmatoare
                    return max_result
                else:
                    #daca sunt pe un nivel interior introc doar scorul si aceiasi tabla
                    return max_result[0], boardd
            else:
                move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char, win_length=win_length)
                return move_score, boardd
        else:  # minimizing level
            if number_of_left_moves(board=boardd) > 0:
                possible_moves = compute_posible_boards(board=boardd, next_char=player_char)
                for pm in possible_moves:
                    results.append(compute_next_move(pm, ai_char, player_char, depth + 1, max_depth,win_length))
                min_result = min(results, key=lambda x: x[0])
                return min_result[0], boardd
            else:
                move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char,win_length=win_length)
                return move_score, boardd


def player_move_is_valid(board: list[list[str]], x: int, y: int) -> bool:
    if x >= len(board) or y >= len(board):
        print(Fore.RED + " COORDONATE INVALIDE! SUNT IN AFARA MATRICII! " + Style.RESET_ALL)
        return False
    if board[x][y] != " ":
        print(Fore.RED + " COORDONATE INVALIDE! CASUTA DEJA POPULATA! " + Style.RESET_ALL)
        return False
    return True

def play_CLI_TicTacToe():
    while True:
        print(Fore.LIGHTYELLOW_EX+"\n----------------- JOC NOU DE X SI O -----------------"+Style.RESET_ALL)
        dim_board = int(input("Introduceti dimensiunea tablei de joc -> "))
        board = [[" " for _ in range(dim_board)] for _ in range(dim_board)]
        dep = int(input("Introduceti adamcimea arborelui de cautare -> "))
        win_length = int(input("Introduceti lungimea secventei de castig -> "))
        player_char = "O"
        ai_char = "X"
        turn = 1
        elapsed_time = 0
        while number_of_left_moves(board) > 0:
            if turn % 2 == 1:   #AI turn
                start_timer()
                board = compute_next_move(board, ai_char="X", player_char="O", depth=0, max_depth=dep,win_length=win_length)[1]
                elapsed_time = stop_timer()
            else:
                while True:
                    lin = int(input("-> Introduceti ce patrat vreti sa populati:\n-> Linie -> "))
                    col = int(input("-> Coloana -> "))
                    if player_move_is_valid(board=board, x=lin - 1, y=col - 1):
                        break
                board[lin - 1][col - 1] = player_char

            print_board(board)

            if turn % 2 == 1:
                print(Fore.BLUE + f"AI-ul fara retezare alfa beta a mutat in: {elapsed_time:.4f} secunde. E randul tau" + Style.RESET_ALL)


            curent_score = evaluate_current_board(board, ai_char=ai_char, player_char=player_char,win_length=win_length)
            if curent_score == -100:
                print(Fore.GREEN + "FELICITARI!! AI CASTIGAT!! INCEARCA O DIFICULTATE MAI MARE!!" + Style.RESET_ALL)
                break
            if curent_score == 100:
                print(Fore.RED + "AI PIERDUT!!" + Style.RESET_ALL)
                break

            turn += 1


if __name__ == '__main__':
    play_CLI_TicTacToe()

