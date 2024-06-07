import numpy as np
import json
import multiprocessing as mp
from collections import defaultdict
import os

# ETR = Estimated Trajectory Return:
    # A number that represents the agents guess at how much reward they can get if they follow that path

def create_initial_qa():
    return defaultdict(float)

agent = 'O' # Whether the Bot plays X or O
enemy = 'X' # The enemy's symbol

alpha = 0.5 # learning rate
gamma = 0.99 # discount factor
epsilon = 0.9 # exploration factor

win_states = [
    {0, 1, 2}, {3, 4, 5}, {6, 7, 8},  # Row Win
    {0, 3, 6}, {1, 4, 7}, {2, 5, 8},  # Column Win
    {0, 4, 8}, {2, 4, 6}  # Diagonal Win
]

def get_possible_actions(state):
    return [i for i, x in enumerate(state) if x == ' ']  # return the indices of all the blank squares

def choose_action(possible_actions, state, Qa, epsilon, player):
    # Explore New Options
    if np.random.uniform(0, 1) < epsilon:
        return np.random.choice(possible_actions)
    # Exploit What We Know
    state_str = ''.join(state)  # Used for indexing into QTable
    if player == agent:
        max_q_value = max([Qa.get(state_str + str(a),0) for a in get_possible_actions(state)]) # the highest return the agent thinks it can get
        max_actions = [a for a in get_possible_actions(state) if Qa.get(state_str + str(a),0) == max_q_value] # the actions that lead to that return
        return np.random.choice(max_actions) # randomly pick between candidate actions
    min_q_value = min([Qa.get(state_str + str(a),0) for a in get_possible_actions(state)]) # the highest return the agent thinks it can get (negative for enemy)
    min_actions = [a for a in get_possible_actions(state) if Qa.get(state_str + str(a),0) == min_q_value] # the actions that lead to that return
    return np.random.choice(min_actions)

def get_next_state(state, action, move):
    next_state = state[:]  # Deep copy
    next_state[action] = move  # alter the state based on the action
    return next_state

def get_reward(state):
    if is_win(state, agent):
        return 1
    if is_win(state, enemy):
        return -1
    if is_draw(state):
        return -0.000001
    return 0

def is_win(state, player):
    squares_filled = {i for i, x in enumerate(state) if x == player}  # list of indices of the squares that the bot has filled
    for i in win_states:
        if squares_filled.intersection(i) == i:  # if the intersection between the set of squares filled and one of the sets of win states *is* the win state, we win
            return True
    return False  # if none of the squares filled matches a win state, return False

def is_draw(state):
    return len([x for x in state if x == ' ']) == 0  # if there are no empty spaces, its a draw. We don't need to check for win/loss because that's checked before.

def update_QTable(state, next_state, action, reward, Qa, player):
    # Hash the state for indexing into QTable
    state_str = ''.join(state)
    next_state_str = ''.join(next_state)

    current_ETR = Qa[next_state_str + str(action)]  # Gets the ETR of the current state and the action taken in that state
    if player == agent:
        next_ETR = current_ETR if len(get_possible_actions(next_state)) == 0 else max([Qa[next_state_str + str(a)] for a in get_possible_actions(next_state)])  # finds the estimated "best" move in the next state
    else:
        next_ETR = current_ETR if len(get_possible_actions(next_state)) == 0 else min([Qa[next_state_str + str(a)] for a in get_possible_actions(next_state)])  # finds the estimated "best" move in the next state
    Qa[state_str + str(action)] = current_ETR + alpha * (reward + gamma * next_ETR - current_ETR)  # basically add the reward plus the change in "goodness" of the path

def train_worker(iterations, epsilon, return_dict, worker_id):
    Qa = create_initial_qa()
    for i in range(iterations):
        state = [' '] * 9  # initial state
        done = False
        if iterations % 1000 == 0:
            epsilon -= 0.001
        while not done:
            for j in range(2):
                possible_actions = get_possible_actions(state)
                action = choose_action(possible_actions, state, Qa, epsilon, agent if j==1 else enemy)
                next_state = get_next_state(state, action, agent if j == 1 else enemy)
                reward = get_reward(next_state)
                update_QTable(state, next_state, action, reward, Qa, agent if j == 0 else enemy)
                state = next_state
                if reward != 0:
                    done = True
                    break
    return_dict[worker_id] = dict(Qa)

def combine_qtables(qtables):
    combined_qtable = create_initial_qa()
    for qtable in qtables:
        for key, value in qtable.items():
            combined_qtable[key] += value
    return combined_qtable

def parallel_train(iterations, num_workers):
    manager = mp.Manager()
    return_dict = manager.dict()
    processes = []
    iters_per_worker = iterations // num_workers
    for i in range(num_workers):
        p = mp.Process(target=train_worker, args=(iters_per_worker, epsilon, return_dict, i))
        processes.append(p)
        p.start()
    for p in processes:
        p.join()

    qtables = [return_dict[i] for i in range(num_workers)]
    combined_qtable = combine_qtables(qtables)
    return combined_qtable

def save(Qa, i):
    os.makedirs("./QTables", exist_ok=True)
    json_string = json.dumps(Qa)
    with open(f"./QTables/Qtable_{i}.json", "w") as outfile:
        outfile.write(json_string)


iterations = 1000000
num_workers = mp.cpu_count() - 1  # use all CPUs except one
if __name__ == "__main__":
    Qa = parallel_train(iterations, num_workers)
    #print(Qa)
    save(Qa, 0)
