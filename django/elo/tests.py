from typing import Any

from elo.models import PlayerBase, GameBase, TestGame
from utils.powerups.inheritance_protection import Uninheritable

from django.db import models
from django.test import TestCase


class EloTest(TestCase):
    def test_game_inheritance_protection(self):
        # This should raise a TypeError because we define an Uninheritable class without intended_use
        with self.assertRaises(TypeError):
            class SomeUninheritableClass(Uninheritable): # pyright: ignore[reportUnusedClass]
                pass

        # This should raise a TypeError because it inherits directly from Game
        with self.assertRaises(TypeError):
            class InvalidGame(GameBase[Any]): # pyright: ignore[reportUnusedClass]
                pass

        # This should succeed because it uses the base_game_model
        class Player(PlayerBase):
            name = models.CharField(max_length=100)

        # Just defining the class to test if it raises an error
        Player.base_game_model()

        # Make sure TestGame is a subclass of Game
        self.assertIsInstance(TestGame.__mro__[1], type(GameBase))