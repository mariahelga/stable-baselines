import numpy as np
from gym import spaces

from stable_baselines.common.vec_env import VecEnvWrapper


class VecFrameStack(VecEnvWrapper):
    def __init__(self, venv, n_stack):
        """
        Vectorized environment base class
        
        :param venv: ([Gym Environment]) the list of environments to vectorize and normalize
        :param n_stack:
        """
        self.venv = venv
        self.n_stack = n_stack
        wos = venv.observation_space  # wrapped ob space
        low = np.repeat(wos.low, self.n_stack, axis=-1)
        high = np.repeat(wos.high, self.n_stack, axis=-1)
        self.stackedobs = np.zeros((venv.num_envs,) + low.shape, low.dtype)
        observation_space = spaces.Box(low=low, high=high, dtype=venv.observation_space.dtype)
        VecEnvWrapper.__init__(self, venv, observation_space=observation_space)

    def step_wait(self):
        obs, rews, news, infos = self.venv.step_wait()
        self.stackedobs = np.roll(self.stackedobs, shift=-obs.shape[-1], axis=-1)
        for (i, new) in enumerate(news):
            if new:
                self.stackedobs[i] = 0
        self.stackedobs[..., -obs.shape[-1]:] = obs
        return self.stackedobs, rews, news, infos

    def reset(self):
        """
        Reset all environments
        """
        obs = self.venv.reset()
        self.stackedobs[...] = 0
        self.stackedobs[..., -obs.shape[-1]:] = obs
        return self.stackedobs

    def close(self):
        self.venv.close()