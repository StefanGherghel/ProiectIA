from colorama import Fore, Style
import threading
import time

timer1 = None  # avem nevoie de 2 timere pentru a cronometra in paralel cei doi algoritmi
timer2 = None


def start_timer1():
    global timer1
    timer1 = time.perf_counter()


def stop_timer1():
    global timer1
    if timer1 is None:
        print("Cronometrul 1 nu a fost pornit!")
        return None
    elapsed_time = (time.perf_counter() - timer1)  # `Secunde`
    timer1 = None  # Resetare
    return elapsed_time


def start_timer2():
    global timer2
    timer2 = time.perf_counter()


def stop_timer2():
    global timer2
    if timer2 is None:
        print("Cronometrul 2 nu a fost pornit!")
        return None
    elapsed_time = (time.perf_counter() - timer2)  # `Secunde`
    timer2 = None  # Resetare
    return elapsed_time


def print_board(board: list[list[str]]):  # board = matricea de joc NxN populata cu "X", "O" sau " "
    print("\n---------- Tabla de joc actuala: ----------\n")
    for i in board:
        print("| ", end="")
        for j in i:
            if j == 'X':
                # pentru vizibiltate, caracterele vor fi printate in culori diferite
                print(Fore.RED + "X" + Style.RESET_ALL, end="")
            elif j == 'O':
                print(Fore.GREEN + "O" + Style.RESET_ALL, end="")
            else:
                print(" ", end="")
            print(" | ", end="")
        print("\n", end="")
    print()


# functia de evaluare a tablei curente. Returneaza +-10 daca castiga AI-ul/Jucatorul.
# In caz ca nu a castigat nimeni returneaza 0
def evaluate_current_board(board: list[list[str]], ai_char: str, player_char: str, win_length: int) -> int:
    n = len(board)  # Dimensiunea tablei

    # Verificare pe linii
    for linie in range(n):
        for start in range(n - win_length + 1):
            if all(board[linie][start + k] == ai_char for k in range(win_length)):
                return 10
            if all(board[linie][start + k] == player_char for k in range(win_length)):
                return -10

    # Verificare pe coloane
    for coloana in range(n):
        for start in range(n - win_length + 1):
            if all(board[start + k][coloana] == ai_char for k in range(win_length)):
                return 10
            if all(board[start + k][coloana] == player_char for k in range(win_length)):
                return -10

    # Verificare pe diagonale principale
    for linie in range(n - win_length + 1):
        for coloana in range(n - win_length + 1):
            if all(board[linie + k][coloana + k] == ai_char for k in range(win_length)):
                return 10
            if all(board[linie + k][coloana + k] == player_char for k in range(win_length)):
                return -10

    # Verificare pe diagonale secundare
    for linie in range(n - win_length + 1):
        for coloana in range(win_length - 1, n):
            if all(board[linie + k][coloana - k] == ai_char for k in range(win_length)):
                return 10
            if all(board[linie + k][coloana - k] == player_char for k in range(win_length)):
                return -10
    return 0


# functie care returneaza nr de spatii ramase pe tabla de joc
def number_of_left_moves(board: list[list[str]]):
    left_spaces = 0
    for line in board:
        for elem in line:
            if elem == " ":
                left_spaces += 1
    return left_spaces


# functie care genereaza toate mutarile posibile ale urmatorului jucator (om/AI)
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


# functie recursiva care foloseste algoritmul minimax FARA retezare alfa beta (varianta clasica)
# returneaza cea mai buna mutare in functie de adancimea arborelui de cautare care a fost setata
def compute_next_AI_move(boardd: list[list[str]], ai_char: str, player_char: str, depth: int, max_depth: int,
                         win_length: int) -> tuple[int, list[list[str]]]:
    results = []
    # evaluarea tablei curente
    move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char, win_length=win_length)
    # daca pe tabla exista un castigator cineva inchei jocul
    if move_score == 100 or move_score == -100:
        return (move_score - depth) if move_score == 100 else (move_score + depth), boardd
    # daca am ajuns la adancimea maxima de cautare ma opresc
    if depth == max_depth:
        move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char,
                                            win_length=win_length)
        return move_score - depth, boardd
    else:
        if depth % 2 == 0:  # daca sunt la un nivel maximizant
            if number_of_left_moves(board=boardd) > 0:
                possible_moves = compute_posible_boards(board=boardd, next_char=ai_char)
                for pm in possible_moves:
                    # generez tot subarborele
                    results.append(compute_next_AI_move(pm, ai_char, player_char, depth + 1, max_depth, win_length))
                # selectez cel mai avatajos scenariu
                max_result = max(results, key=lambda x: x[0])
                if depth == 0:
                    # daca sunt pe primul nivel de arbore intorc tabla urmatoare
                    return max_result
                else:
                    # daca sunt pe un nivel interior introc doar scorul si aceiasi tabla
                    return max_result[0], boardd
            else:
                move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char,
                                                    win_length=win_length)
                return move_score, boardd
        else:  # minimizing level
            if number_of_left_moves(board=boardd) > 0:
                possible_moves = compute_posible_boards(board=boardd, next_char=player_char)
                for pm in possible_moves:
                    results.append(compute_next_AI_move(pm, ai_char, player_char, depth + 1, max_depth, win_length))
                min_result = min(results, key=lambda x: x[0])
                return min_result[0], boardd
            else:
                move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char,
                                                    win_length=win_length)
                return move_score, boardd


def compute_next_AI_move_ab_pruning(boardd: list[list[str]], ai_char: str, player_char: str, depth: int,
                                    max_depth: int, win_length: int, alpha: int, beta: int) \
        -> tuple[int, list[list[str]]]:
    results = []
    # evaluarea tablei curente
    move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char, win_length=win_length)
    # daca pe tabla exista un castigator inchei jocul
    if move_score == 100 or move_score == -100:
        return (move_score - depth) if move_score == 100 else (move_score + depth), boardd
    # daca am ajuns la adancimea maxima de cautare ma opresc
    if depth == max_depth:
        move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char,
                                            win_length=win_length)
        return move_score - depth, boardd
    else:
        if depth % 2 == 0:  # daca sunt la un nivel maximizant
            if number_of_left_moves(board=boardd) > 0:
                possible_moves = compute_posible_boards(board=boardd, next_char=ai_char)
                max_result = None
                for pm in possible_moves:
                    # generez tot subarborele
                    results.append(compute_next_AI_move_ab_pruning(pm, ai_char, player_char, depth + 1,
                                                                   max_depth, win_length, alpha, beta))
                    max_result = max(results, key=lambda x: x[0])  # <- aici intervine retezarea alfa beta
                    alpha = max(alpha, max_result[0])
                    if beta < alpha:
                        break  # <- aici se opreste secventa alfa beta
                if depth == 0:
                    # daca sunt pe primul nivel de arbore intorc tabla urmatoare
                    return max_result
                else:
                    # daca sunt pe un nivel interior introc doar scorul si aceiasi tabla
                    return max_result[0], boardd
            else:
                move_score = evaluate_current_board(board=boardd, ai_char=ai_char,
                                                    player_char=player_char, win_length=win_length)
                return move_score, boardd
        else:  # minimizing level
            if number_of_left_moves(board=boardd) > 0:
                possible_moves = compute_posible_boards(board=boardd, next_char=player_char)

                min_result = None
                for pm in possible_moves:
                    results.append(compute_next_AI_move_ab_pruning(pm, ai_char, player_char,
                                                                   depth + 1, max_depth, win_length, alpha, beta))
                    min_result = min(results, key=lambda x: x[0])  # <- aici intervine retezarea alfa beta
                    beta = min(beta, min_result[0])
                    if beta <= alpha:
                        break  # <- aici se opreste secventa alfa beta

                return min_result[0], boardd
            else:
                move_score = evaluate_current_board(board=boardd, ai_char=ai_char, player_char=player_char,
                                                    win_length=win_length)
                return move_score, boardd


def player_move_is_valid(board: list[list[str]], x: int, y: int) -> bool:
    if x >= len(board) or y >= len(board):
        print(Fore.RED + " COORDONATE INVALIDE! SUNT IN AFARA TABLEI DE JOC! " + Style.RESET_ALL)
        return False
    if board[x][y] != " ":
        print(Fore.RED + " COORDONATE INVALIDE! CASUTA DEJA POPULATA! " + Style.RESET_ALL)
        return False
    return True


# functie care verifica daca jocul este incheiat si afiseaza un mesaj conform rezutatului. Returneaza 1 in caz ca jocul
# s-a terminat. 0 altfel
def game_over_with_message(score: int) -> int:
    if score == -10:
        print(Fore.GREEN + r"""
                 \o/
                  |
                 / \
    BRAVO!AI CASTIGAT! AI BATUT AI_UL!!""" + Style.RESET_ALL)
        return 1
    if score == 10:
        print(Fore.RED + r"""
             __________
           /            \
          |,  .-.  .-.  ,|
          | )(_o/  \o_)( |
          |/     /\     \|
          (_     ^^     _)
           \__|IIIIII|__/
            | \IIIIII/ |
            \          /
             `--------`
       GATA JOCUL! AI PIERDUT!""" + Style.RESET_ALL)
        return 1
    return 0


# functie utilzata pentru a marca finalul turei ai-ului si pentru a afisa timpul necesar rularii algoritmului
def print_end_of_ai_turn_message(game_mode: int, elapsed_time1: float, elapsed_time2: int):
    if game_mode == 0:  # minimax clasic
        print(Fore.BLUE + f"AI-ul FARA retezare alfa beta a mutat in: " + Fore.YELLOW + f"{elapsed_time1:.4f} "
              + Fore.BLUE + f"secunde. E randul tau" + Style.RESET_ALL)
    if game_mode == 1:  # minimax alfa beta pruning
        print(Fore.BLUE + f"AI-ul CU retezare alfa beta a mutat in: " + Fore.YELLOW + f" {elapsed_time1:.4f} "
              + Fore.BLUE + f"secunde. E randul tau" + Style.RESET_ALL)
    if game_mode == 2:  # rulare ambii algoritmi in paralel
        print(Fore.BLUE +
              f"MINIMAX FARA retezare alfa beta a durat:" + Fore.YELLOW + f" {elapsed_time1:.4f} " + Fore.BLUE +
              f"secunde.\nMINIMAX CU retezare alfa beta a mutat in:" + Fore.YELLOW + f" {elapsed_time2:.4f} " + Fore.BLUE +
              "secunde.\n-> E randul tau!\n" +
              Style.RESET_ALL)


# functia care se ocupa de logica jocului
def play_CLI_TicTacToe():
    # bucla infinita a jocului
    while True:
        # initial jucatorului ii sunt cerute dimensiunea tablei de joc, lungimea secventei de castig si adancime arbore
        print(Fore.LIGHTYELLOW_EX + "\n----------------- JOC NOU DE X SI O -----------------" + Style.RESET_ALL)
        dim_board = int(input("Introduceti dimensiunea tablei de joc -> "))
        board = [[" " for _ in range(dim_board)] for _ in range(dim_board)]
        dep = int(input("Introduceti adamcimea arborelui de cautare -> "))
        win_length = int(input("Introduceti lungimea secventei de castig -> "))
        game_mode = int(input(
            "Modelul de AI: 0 = minimax, 1 = minimax alfa beta pruning, 2 = ambele in comparatie -> "))
        player_char = "O"
        ai_char = "X"
        turn = 1
        elapsed_time1 = 0
        elapsed_time2 = 0
        while number_of_left_moves(board) > 0:
            if turn % 2 == 1:   # randul ai-ului sa mute
                if game_mode == 0:
                    start_timer1()
                    board = compute_next_AI_move(board, ai_char="X", player_char="O", depth=0, max_depth=dep,
                                                 win_length=win_length)[1]
                    elapsed_time1 = stop_timer1()
                if game_mode == 1:
                    start_timer1()
                    board = compute_next_AI_move_ab_pruning(board, ai_char="X", player_char="O", depth=0, max_depth=dep,
                                                            win_length=win_length, alpha=-1000, beta=+1000)[1]
                    elapsed_time1 = stop_timer1()
                if game_mode == 2:
                    thread_minimax_normal = threading.Thread(target=compute_next_AI_move, args=(board, "X", "O", 0, dep,
                                                                                                win_length))
                    start_timer1()
                    thread_minimax_normal.start()
                    start_timer2()
                    board = compute_next_AI_move_ab_pruning(board, ai_char="X", player_char="O", depth=0, max_depth=dep,
                                                            win_length=win_length, alpha=-1000, beta=+1000)[1]
                    elapsed_time2 = stop_timer2()

                    thread_minimax_normal.join()
                    elapsed_time1 = stop_timer1()
            else:   # randul jucatorului sa mute
                while True:
                    lin = int(input("-> Introduceti ce patrat vreti sa populati:\n-> Linie -> "))
                    col = int(input("-> Coloana -> "))
                    if player_move_is_valid(board=board, x=lin - 1, y=col - 1):
                        break
                board[lin - 1][col - 1] = player_char

            print_board(board)

            # afisare informatii despre tura ai-ului
            if turn % 2 == 1:
                print_end_of_ai_turn_message(game_mode, elapsed_time1, elapsed_time2)

            current_score = evaluate_current_board(board, ai_char=ai_char, player_char=player_char,
                                                   win_length=win_length)

            if game_over_with_message(current_score) == 1:
                break

            turn += 1


if __name__ == '__main__':
    play_CLI_TicTacToe()
