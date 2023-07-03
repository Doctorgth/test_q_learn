import numpy as np

# Определение среды
num_states = 6# число различных состояний которые возвращает среда агенту
num_actions = 2
reward_matrix = np.array([[0, -10], [-1, -1], [-1, -1], [-1, -1], [-10, 0], [0, 0]])
q_matrix = np.zeros((num_states, num_actions))

# Параметры обучения
learning_rate = 0.1
discount_factor = 0.9
num_episodes = 1000

# Алгоритм Q-обучения
for episode in range(num_episodes):
    state = np.random.randint(0, num_states)#текущее состояние среды на момент совершения действия агентом

    while state != 5:#пока среда не вернет достижение цели
        action = np.argmax(q_matrix[state])
        next_state = np.random.choice(range(num_states))#возвращается средой как ответ на действие агента

        reward = reward_matrix[state][action]#сюда среда отдавала бы награду как ответ на действие агента
        q_value = q_matrix[state][action]#берется значение соответствующее состоянию в которое попал агент и его действию в этой ситуации

        max_q_next = np.max(q_matrix[next_state])
        new_q_value = q_value + learning_rate * (reward + discount_factor * max_q_next - q_value)
        q_matrix[state][action] = new_q_value

        state = next_state

# Результаты обучения
print("Матрица Q-значений:")
print(q_matrix)