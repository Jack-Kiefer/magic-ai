import mtg_env
from pettingzoo.test import api_test

env = mtg_env.mtg_env()
api_test(env, num_cycles=1000, verbose_progress=False)