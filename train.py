import time
import argparse  # Import argparse for command-line arguments

from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.policies import MaskableActorCriticPolicy
from sb3_contrib.common.wrappers import ActionMasker

import pettingzoo.utils
import mtg_env_v0

class SB3ActionMaskWrapper(pettingzoo.utils.BaseWrapper):
    """Wrapper to allow PettingZoo environments to be used with SB3 illegal action masking."""

    def reset(self, seed=None, options=None):
        """Gymnasium-like reset function which assigns obs/action spaces to be the same for each agent.

        This is required as SB3 is designed for single-agent RL and doesn't expect obs/action spaces to be functions
        """
        super().reset(seed, options)

        # Strip the action mask out from the observation space
        self.observation_space = super().observation_space(self.possible_agents[0])
        self.action_space = super().action_space(self.possible_agents[0])

        # Return initial observation, info (PettingZoo AEC envs do not by default)
        return self.observe(self.agent_selection), {}

    def step(self, action):
        """Gymnasium-like step function, returning observation, reward, termination, truncation, info."""
        super().step(action)
        return super().last()

    def observe(self, agent):
        """Return only raw observation, removing action mask."""
        return super().observe(agent)["observation"]

    def action_mask(self):
        """Separate function used in order to access the action mask."""
        return super().observe(self.agent_selection)["action_mask"]

def mask_fn(env):
    # Do whatever you'd like in this function to return the action mask
    # for the current env. In this example, we assume the env has a
    # helpful method we can rely on.
    mask = env.action_mask()
    return mask

def linear_schedule(initial_value):
    """
    Creates a function that returns a linearly decreasing learning rate from the initial value.
    """
    def func(progress_remaining):
        return progress_remaining * initial_value
    return func

def rewardFn(life, mana, cards):
    if life <= 0:
        return -1000
    else:
        return life * (10 / life) + 50 * cards + 2 * mana

def train_action_mask(env_fn, steps=10_000, seed=0, initial_learning_rate=0.002, **env_kwargs):
    """Train a single model to play as each agent in a zero-sum game environment using invalid action masking."""
    env = env_fn.env(**env_kwargs)

    print(f"Starting training on {str(env.metadata['name'])}.")

    # Custom wrapper to convert PettingZoo envs to work with SB3 action masking
    env = SB3ActionMaskWrapper(env)

    env.reset(seed=seed)  # Must call reset() in order to re-define the spaces

    env = ActionMasker(env, mask_fn)  # Wrap to enable masking (SB3 function)

    learning_rate = linear_schedule(initial_learning_rate)

    model = MaskablePPO(
        MaskableActorCriticPolicy,
        env,
        verbose=1,
        learning_rate=learning_rate,
    )

    model.set_random_seed(seed)
    model.learn(total_timesteps=steps)

    model.save(f"{env.unwrapped.metadata.get('name')}_{time.strftime('%Y%m%d-%H%M%S')}")

    print("Model has been saved.")

    print(f"Finished training on {str(env.unwrapped.metadata['name'])}.\n")

    env.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a Magic: The Gathering AI using Stable-Baselines3.")
    parser.add_argument("--steps", type=int, default=10000, help="Number of training steps")
    parser.add_argument("--learning_rate", type=float, default=0.002, help="Initial learning rate for training")

    args = parser.parse_args()

    env_fn = mtg_env_v0

    env_kwargs = {'rewardFn': rewardFn}

    # Train a model with the specified parameters
    train_action_mask(env_fn, steps=args.steps, seed=0, initial_learning_rate=args.learning_rate, **env_kwargs)
