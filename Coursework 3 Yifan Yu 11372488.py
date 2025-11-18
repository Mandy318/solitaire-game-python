"""
MATH20621 - Coursework 3
Student name: Yifan Yu
Student id:   11372488
Student mail: yifan.yu-8@student.manchester.ac.uk
"""


def display_state(s, *, clear=False):
    """
    Display the state s

    If 'clear' is set to True, erase previous displayed states
   """
    def colored(r, g, b, text):
        rb,gb,bb=(r+2)/3,(g+2)/3,(b+2)/3
        rd,gd,bd=(r)/1.5,(g)/1.5,(b)/1.5
        return f"\033[38;2;{int(rb*255)};{int(gb*255)};{int(bb*255)}m\033[48;2;{int(rd*255)};{int(gd*255)};{int(bd*255)}m{text}\033[0m"

    def inverse(text):
        rb,gb,bb=.2,.2,.2
        rd,gd,bd=.8,.8,.8
        return f"\033[38;2;{int(rb*255)};{int(gb*255)};{int(bb*255)}m\033[48;2;{int(rd*255)};{int(gd*255)};{int(bd*255)}m{text}\033[0m"

    colours = [(1.0, 0.349, 0.369),
               (1.0, 0.573, 0.298),
               (1.0, 0.792, 0.227),
               (0.773, 0.792, 0.188),
               (0.541, 0.788, 0.149),
               (0.322, 0.651, 0.459),
               (0.098, 0.509, 0.769),
               (0.259, 0.404, 0.675),
               (0.416, 0.298, 0.576)]

    n_columns = len(s['stacks'])
    if clear:
        print(chr(27) + "[2J")

    print('\n')
    row = 0
    numrows = max(len(stack) for stack in s['stacks'])
    for row in range(numrows-1,-1,-1):
        for i in range(n_columns):
            num_in_col = len(s['stacks'][i])
            if num_in_col > row:
                val = s['stacks'][i][row]
                if num_in_col == row+1 and s['blocked'][i]:
                    print(inverse(' '+str(val)+' '),end=' ')
                else:
                    if s['complete'][i]:
                        print(colored(*colours[val-1],'   '),end=' ')
                    else:
                        print(colored(*colours[val-1],' '+str(val)+' '),end=' ')
            else:
                print('    ',end='')
        print()
    print(' A   B   C   D   E   F')

# Q1
def initial_state():
    """
    Generates the initial game state with shuffled cards and empty blocked/complete flags.
    Returns:
        dict: A dictionary representing the initial state of the game with keys:
            - 'stacks': A list of lists representing the stacks of cards.
            - 'blocked': A list of booleans indicating if the stack is blocked.
            - 'complete': A list of booleans indicating if the stack is complete.

    """
    import random # Import the random module
    # Generate the cards (4 copies each of 1-9)
    cards = [i for i in range(1, 10)] * 4  # Create 4 copies of cards 1-9
    random.shuffle(cards) # Shuffle the cards randomly

    # Divide cards into six stacks, each containing 6 cards.
    stacks = [cards[i:i + 6] for i in range(0, 36, 6)]

    # Initial blocked and complete states
    state = {
        'stacks': stacks,
        'blocked': [False,False,False,False,False,False] ,  # No stack is blocked initially
        'complete': [False,False,False,False,False,False]  # No stack is complete initially
    }
    return state  # Return the initial game state
    

# Q2
def parse_move(input_str):
    """
    Parses user input into a move tuple (source_stack, destination_stack, num_cards).
    Handles the following cases:
    - Raises ValueError for invalid input formats (Q6).
    - Returns 0 for resetting the game ('R' or 'r') (Q7).
    - Returns -1 for undoing moves ('U' or 'u') (Q8).
    """
    # Map letters A-F to indices 0-5
    letter_to_index = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5}

    parts = input_str.strip().upper()# Remove extra spaces and convert to uppercase

    if parts == 'R':
        return 0  # Reset game
    elif parts == 'U':
        return -1  # Undo last move
    elif len(parts) >= 2: # Check for valid move inputs
        if parts[0] not in letter_to_index or parts[1] not in letter_to_index:
            raise ValueError # Source and destination must be between A and F.

        src = letter_to_index[parts[0]] # Convert source stack letter to index
        dest = letter_to_index[parts[1]] # Convert destination stack letter to index

       # Validate and parse the number of cards
        if len(parts) > 2:
            if not parts[2:].isdigit():  # If the third part exists, ensure it's a digit
                raise ValueError("The number of cards must be a positive integer.")
            num_cards = int(parts[2:]) # Convert the number part to an integer
        else:
            num_cards = 1  # Default to 1 card if no number is specified.
            
        return (src, dest, num_cards) # Return the parsed move as a tuple

    raise ValueError # Invalid input format. Must be two letters optionally followed by a number.


# Q3
def validate_move(state, move):
    """
    Validates a move to ensure it adheres to the game rules.
    
    Rules:
    - The source stack must contain enough cards to move.
    - The source stack must not be blocked or complete. Besides moving the blocking card.
    - The destination stack must not be blocked or complete.
    - If moving multiple cards, they must form a descending sequence.
    - The last card moved (top of the source stack) must match the rule for the destination stack:
      - The destination stack is empty, or
      - The destination stack's top card is exactly one more than the source stack's bottom card.
    - If the source stack is blocked, the blocking card can only be moved to:
      1. An empty stack.
      2. A stack whose top card is larger than the blocking card by 1.
    """
    source, dest, num_cards = move

    # Rule: Source stack must have enough cards
    if len(state['stacks'][source]) < num_cards:
        return False

    # Rule: Source stack must not be blocked
    if state['blocked'][source] and num_cards != 1: # removing the blocking card on top is allowed
        return False
    
    # Rule: Source stack must not be complete
    if state['complete'][source]:
       return False

    # Rule: Destination stack must not be complete
    if state['complete'][dest]:
        return False

    # Rule: Moving multiple cards requires a descending and continuous sequence
    if num_cards > 1:
     cards_to_move = state['stacks'][source][-num_cards:]
     if cards_to_move != sorted(cards_to_move, reverse=True):
       return False
    # Check if the cards are continuous
     for i in range(len(cards_to_move) - 1):
       if cards_to_move[i] - cards_to_move[i + 1] != 1:
           return False
       
    # Destination stack must not be blocked
    if state['blocked'][dest]:
        return False
    
    # Special handling for blocked source stacks
    dest_stack = state['stacks'][dest]
    if state['blocked'][source]: 
        if len(dest_stack) == 0:# Can move to empty stack
            return True
        top_dest_card = dest_stack[-1]
        blocking_card = state['stacks'][source][-1]
        return blocking_card == top_dest_card - 1  # Must be one less than destination
    
    # Check stacking rules for destination stack
    if dest_stack:
        top_dest_card = dest_stack[-1]
        bottom_moved_card = state['stacks'][source][-num_cards]  
        if bottom_moved_card != top_dest_card - 1:
            if num_cards == 1:
                # Single card can be moved as a blocking move
                return True
            else:
                # Cannot move multiple cards if stacking rule is not satisfied
                return False
    else:
        # Destination stack is empty
        return True

    # Game rules are satisfied
    return True

# Q4
def apply_move(state, move):
    """
    Applies a move to the game state, including handling sigle/multiple card moves, blocking moves and complete stacks.
    Modifies the state in place.
    """
    source, dest, num_cards = move

    # Remove cards from the source stack
    cards_to_move = state['stacks'][source][-num_cards:]
    state['stacks'][source] = state['stacks'][source][:-num_cards]

    # Add cards to the destination stack
    state['stacks'][dest].extend(cards_to_move)
    dest_stack = state['stacks'][dest]
    
    # Reset all blocked statuses
    state['blocked'][source] = False
    state['complete'][dest] = state['stacks'][dest] == list(range(9,0,-1))# Check if complete

    # Determine if destination stack becomes blocked
    if num_cards == 1 and len(dest_stack) > 1:
        moved_card = dest_stack[-1]
        below_card = dest_stack[-2]
        if moved_card != below_card - 1:
            # Blocking move: The moved card does not follow stacking rules
            state['blocked'][dest] = True
        else:
            state['blocked'][dest] = False  # Not a blocking move
            
    # Update 'complete' statuses
    for i in range(len(state['stacks'])):
        stack = state['stacks'][i]
        if len(stack) == 9 and stack == list(range(9,0,-1)):  # Stack is complete
            state['complete'][i] = True
            state['blocked'][i] = False  # A complete stack cannot be blocked
        else:
            state['complete'][i] = False

# Q5
def game_won(state):
    """
    Determines if the game has been won.

    The game is considered won if exactly 4 stacks are completed with
    9 cards each (arranged in descending order from 9 to 1) and the other
    2 stacks are empty.

    Parameters:
    - state: The current game state, including stacks, blocked, and complete fields.

    Returns:
    - bool: True if the game is won, False otherwise.
    """
    complete_count = 0
    empty_count = 0

    # Iterate through each stack to check conditions
    for i in range(len(state['stacks'])):
        stack = state['stacks'][i]
        is_complete = state['complete'][i]
        if is_complete and stack == list(range(9, 0, -1)):  # Check if stack is complete
            complete_count += 1
        elif len(stack) == 0:  # Check if stack is empty
            empty_count += 1
        else:
            return False  # If a stack is neither complete nor empty, the game is not won

    # The game is won if exactly 4 stacks are complete and 2 stacks are empty
    if complete_count == 4 and empty_count == 2:
      return True
    else:
      return False
# For questions 1-5, DO NOT edit the play_game function.
# For the tasks in questions 1-5 initial_state, parse_move,
# validate_move, apply_move, and game_won must work with the
# the unmodified play_game function.

# For questions 6, 7 and 8, you should modify the play_game
# function


def play_game():
    # When we start the game,
    board = initial_state()
    move_history = []  # To track the history of moves for undo functionality
    try:
        while True:
            # Display the current game state
            display_state(board, clear=False)

            # Read input from the user.
            # (Do not alter this line, even in questions 6, 7, 8.)
            move_str = input()

            try:
                # Parse the text typed by the user and convert it to a move
                move = parse_move(move_str)

                # Handle resetting the game
                if move == 0:
                    board = initial_state()
                    move_history.clear()
                    continue

                # Handle undoing the last move
                elif move == -1:
                    if move_history:
                        board = move_history.pop()
                    else:
                        print("No moves to undo.")
                    continue 

                # If the move was valid...
                if validate_move(board, move):
                    move_history.append({'stacks': [list(stack) for stack in board['stacks']], 'blocked': list(board['blocked']), 'complete': list(board['complete'])})
                    apply_move(board, move)  # ... alter the board

                    # If we've won, end the game
                    if game_won(board):
                        display_state(board, clear=False)
                        print("Congratulations, you've won!")
                        break
                else:
                    print("Invalid move. Please try again.")

            except ValueError as e:
                print(e) # Handle invalid input

    except KeyboardInterrupt:  # If the user presses Ctrl-C, quit
        pass



play_game()

