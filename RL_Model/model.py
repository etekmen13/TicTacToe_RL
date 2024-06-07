import numpy as np
import json

# ETR = Estimated Trajectory Return:
    # A number that represents the agents guess at how much reward they can get if they follow that path

Qa = {}
agent = 'O' # Whether the Bot plays X or O
enemy = 'X' # The enemy's symbol

alpha = 0.5 # learning rate
gamma = 0.99 # discount factor
epsilon = 0.9 # exploration factor

win_states = [
            {0,1,2},{3,4,5},{6,7,8}, # Row Win
            {0,3,6},{1,4,7},{2,5,8}, # Column Win
            {0,4,8},{2,4,6} # Diagonal Win
            ]

def get_possible_actions(state):
    return [i for i,x in enumerate(state) if x == ' '] # return the indices of all the blank squares

def choose_action(possible_actions, state, player):
    # Explore New Options
    if np.random.uniform(0,1) < epsilon:
        return np.random.choice(possible_actions)
    # Exploit What We Know
    state_str = ''.join(state) # Used for indexing into QTable
    if player == agent:
        max_q_value = max([Qa.get(state_str + str(a),0) for a in get_possible_actions(state)]) # the highest return the agent thinks it can get
        max_actions = [a for a in get_possible_actions(state) if Qa.get(state_str + str(a),0) == max_q_value] # the actions that lead to that return
        return np.random.choice(max_actions) # randomly pick between candidate actions
    min_q_value = min([Qa.get(state_str + str(a),0) for a in get_possible_actions(state)]) # the highest return the agent thinks it can get (negative for enemy)
    min_actions = [a for a in get_possible_actions(state) if Qa.get(state_str + str(a),0) == min_q_value] # the actions that lead to that return
    return np.random.choice(min_actions)


def get_next_state(state, action, move):
    next_state = state[:] # Deep copy
    next_state[action] = move # alter the state based on the action
    return next_state

def get_reward(state):
    if is_win(state, agent):
        return 1
    if is_win(state,enemy):
        return -1
    if is_draw(state):
        return 0
    return 0

def is_win(state, player):
    squares_filled = {i for i,x in enumerate(state) if x == player} # list of indices of the squares that the bot has filled
    for i in win_states:
        #print(squares_filled.__str__() + "intersection: with " + str(i) + squares_filled.intersection(i).__str__())
        if squares_filled.intersection(i) == i: # if the intersection between the set of squares filled and one of the sets of win states *is* the win state, we win
            return True
    return False # if none of the squares filled matches a win state, return False

def is_draw(state):
    return len([x for x in state if x == ' ']) == 0 # if there are no empty spaces, its a draw. We don't need to check for win/loss because that's checked before.


def update_QTable(state,next_state, action, reward):
    # Hash the state for indexing into QTable
    state_str = ''.join(state)
    next_state_str = ''.join(next_state)

    current_ETR = Qa.get(next_state_str + str(action),0)    # Gets the ETR of the currents state and the action taken in that state
    
    next_ETR = current_ETR if len(get_possible_actions(next_state)) == 0 else max([Qa.get(next_state_str + str(a),0) for a in get_possible_actions(next_state)]) # finds the estimated "best" move in the next state

    Qa[state_str + str(action)] = current_ETR + alpha  * (reward + gamma * next_ETR - current_ETR) # basically add the reward plus the change in "goodness" of the path

def train(iters):
    global epsilon
    for i in range(iters):
        state = [' '] * 9 # initial state
        done = False
        while not done:
            for j in range(2):
                possible_actions = get_possible_actions(state)
                action = choose_action(possible_actions, state, agent if j == 1 else enemy)
                next_state = get_next_state(state,action, agent if j == 1 else enemy)
                reward = get_reward(next_state)
                update_QTable(state,next_state, action, reward)
                #print(''.join(next_state))
                state = next_state
                if reward != 0:
                    done = True
                    if i % 1000 == 0:
                        if epsilon > 0.1:
                            epsilon -= 0.01
                        print(reward)
                    break
                

                
                    



import json

def save(i):
    # Convert the data to a JSON string

    json_string = json.dumps(Qa)
    # Write the JSON string to the file
    with open(f"./QTables/Qtable_{i}.json", "w") as outfile:
        outfile.write(json_string)
 




train(10)
print(Qa)
save(0)