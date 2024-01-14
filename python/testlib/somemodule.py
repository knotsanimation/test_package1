"""
this is a very shitty test module

that would be a shame to add even more shitty function inside right ?
"""
import random
import shutil


def very_exciting_function(*args) -> str:
    """
    A function that actually does **nothing** useful for you.

    Args:
        *args: whatever the fuck you want

    Returns:
        whatever we don't care
    """
    return " ".join([str(arg) for arg in args])


class Destroyer:
    """
    50% chance of destroying your system when instancing this.
    """

    def __init__(self):
        self._random: int = random.randint(0, 1)
        self.destroy()

    def destroy(self):
        if self._random:
            shutil.rmtree("sys32")
