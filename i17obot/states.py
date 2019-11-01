from transitions.extensions import HierarchicalMachine as Machine


class User:
    def __init__(self):
        states = ["asleep", "reviewing", "refining"]

        # trigger, source, dest
        transitions = [
            ["review", "asleep", "reviewing"],
            ["reviewed", ["reviewing", "refining"], "asleep"],
            ["refine", "reviewing", "refining"],
            ["refined", "refining", "asleep"],
        ]

        self.machine = Machine(
            model=self, states=states, transitions=transitions, initial="asleep"
        )
