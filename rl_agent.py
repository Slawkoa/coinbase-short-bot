import numpy as np
class RLAgent:
    def __init__(self, model_path: str):
        self.model_path = model_path
        # self.model = load_model(model_path)

    def select_action(self, state: np.ndarray) -> str:
        # Placeholder: always short
        return 'short'

    def update(self, state: np.ndarray, action: str, reward: float):
        pass
