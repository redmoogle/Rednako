import requests
import random

"""
Taken from https://github.com/Pythonastics/animals.py/blob/master/animals/client.py

Did it because it needs bugfixes
"""


class Animals:
    """
    Base Class for the module. This module uses https://some-random-api.ml/.
    This module can be used to get random animals image/fact.
    This is a simple module, which uses requests library.

    Attributes
    ---------------

    image
        Returns the url of the animal image

        Parameters
        ------------------
        animal: :class: `str`
            The animal which you are going to get the url.
            If not animal given it will give a random image.

    fact
        Return the fact of the animal image

        Parameters
        ------------------
        animal: :class: `str`
            The animal which you are going to get the fact.
            If not animal given it will give a random fact
    """

    def __init__(self, animal):
        self.animal = animal

    def image(self):
        """Returns the image url of the animal"""
        options = ("cat", "dog", "koala", "fox", "birb", "red_panda", "panda", "racoon", "kangaroo")
        if self.animal is None:
            self.animal = random.choice(options)
        if self.animal not in options:
            return False
        r = requests.get("https://some-random-api.ml/img/" + self.animal)
        r = r.json()
        return r["link"]

    def fact(self):
        """Returns the fact of the animal"""
        options = ("cat", "dog", "panda", "koala", "fox", "bird", "racoon", "kangaroo", "elephant", "giraffe", "whale")
        if not self.animal:
            self.animal = random.choice(options)
        if self.animal not in options:
            return False
        r = requests.get("https://some-random-api.ml/facts/" + self.animal)
        r = r.json()
        return r["fact"]
