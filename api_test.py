import mtg_env
from pettingzoo.test import api_test

# env = mtg_env.mtg_env()
# api_test(env, num_cycles=1000, verbose_progress=False)

def debug_environment(env):
    """
    Run a debugging session for the given environment.
    """
    env.reset()
    try:
        while True:
            print("\nCurrent Environment State:")
            env.render()  # Ensure the environment has a render method to visualize state

            if any(env.terminations.values()):
                print("Game has ended.")
                break

            agent = env.agent_selection
            print(f"Current agent: {agent}")

            print(f"Current phase: {env.state.phase}")

            # Display action choices and mask
            action_mask = env.infos[agent]['action_mask']
            print("Available actions:")
            for i, available in enumerate(action_mask):
                if available:
                    action_desc, _ = env.mask_to_action(i)
                    print(f"{i}: {action_desc}")

            # User chooses an action
            if sum(action_mask) == 1:
                env.step(0)
            else:
                valid_input = False
                while not valid_input:
                    try:
                        action = int(input("Enter your action: "))
                        if action < 0 or action >= env.action_space(agent).n:
                            raise ValueError("Action out of bounds.")
                        if action_mask[action] == 0:
                            raise ValueError("Action not allowed.")
                        valid_input = True
                    except ValueError as e:
                        print(str(e))
                        continue

                # Perform the chosen action
                env.step(action)
                print(f"Action taken: {env.mask_to_action(action)}")

    except KeyboardInterrupt:
        print("Debugging interrupted by user.")

# Usage example:
if __name__ == "__main__":
    environment = mtg_env.raw_env()
    api_test(environment, num_cycles=1000, verbose_progress=False)
    #debug_environment(environment)
