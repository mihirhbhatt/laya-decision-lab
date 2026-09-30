import laya


class LayaEngine:

    def __init__(self, model=None, device=None):
        self.model = model
        self.device = device
        self.agent = None

    def load(self):
        if self.agent is None:
            if self.model is None:
                self.agent = laya.Router(device=self.device)
            else:
                self.agent = laya.load(self.model, device=self.device)

        return self.agent

    def predict(self, state, questions):
        agent = self.load()
        return agent.predict(state, questions)