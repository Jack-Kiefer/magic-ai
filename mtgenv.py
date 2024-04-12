import gym
from gym import spaces
import numpy as np
import random
import game

#%%
class MTGEnv(gym.Env):
    def __init__(self):
        super(MTGEnv, self).__init__()
        # Assuming a maximum of 20 creatures and 20 lands can be played
        self.action_space = spaces.Discrete(40)  # 20 creatures and 20 lands
        self.observation_space = spaces.Dict({
            "hand": spaces.MultiBinary(40),  # Representation of the hand
            "creatures": spaces.Box(low=0, high=20, shape=(20, 3), dtype=np.int32),  # (power, toughness, tapped)
            "lands": spaces.Discrete(20),
            "life": spaces.Discrete(21)  # Player life from 0 to 20
        })

        self.deck = [game.Creature("Bear", 2, 2, 2) for _ in range(20)] + [Land("Forest") for _ in range(20)]
        random.shuffle(self.deck)
        self.state = GameState(self.deck, "AI Player", seed=0, scorefn=lambda x: x.life)

    def reset(self):
        self.state = GameState(self.deck, "AI Player", seed=random.randint(0, 1000), scorefn=lambda x: x.life)
        return self._get_obs()

    def _get_obs(self):
        # Simplified observation (one-hot encode hand and other elements)
        hand_representation = [0] * 40
        for card in self.state.hand:
            index = self.deck.index(card)
            hand_representation[index] = 1

        creature_info = np.zeros((20, 3))
        for i, creature in enumerate(self.state.creatures):
            creature_info[i] = [creature.power, creature.toughness, creature.tapped]

        return {
            "hand": np.array(hand_representation),
            "creatures": creature_info,
            "lands": self.state.totalLands,
            "life": self.state.life
        }

    def step(self, action):
        card = self.deck[action]  # Translate action to card
        self.state.playCard(card)
        done = self.state.life <= 0 or len(self.state.deck) == 0
        reward = self.state.scorefn(self.state)
        return self._get_obs(), reward, done, {}

    def render(self, mode='human'):
        print(f"Player Life: {self.state.life}")
        print("Hand:", self.state.hand)
        print("Creatures on Field:", self.state.creatures)


# Hyperparameters
alpha = 0.1
gamma = 0.6
epsilon = 0.1

# Initialize Q-table
q_table = np.zeros([env.observation_space.n, env.action_space.n])

# Training loop
for i in range(1, 10001):
    state = env.reset()
    epochs, penalties, reward, = 0, 0, 0
    done = False

    while not done:
        if random.uniform(0, 1) < epsilon:
            action = env.action_space.sample()  # Explore action space
        else:
            action = np.argmax(q_table[state])  # Exploit learned values

        next_state, reward, done, info = env.step(action)

        old_value = q_table[state, action]
        next_max = np.max(q_table[next_state])

        new_value = (1 - alpha) * old_value + alpha * (reward + gamma * next_max)
        q_table[state, action] = new_value

        state = next_state
        epochs += 1

print("Training finished.\n")