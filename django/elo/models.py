from typing import Any, Generic, TypeVar

from utils.django import DynamicField

from django.db import models


class Eloable(models.Model):

    class Meta:
        abstract = True

    DEFAULT_ELO = 1000.0
    K_FACTOR = 32.0

    elo: 'models.FloatField[float]' = DynamicField(
        models.FloatField, lambda: Eloable,
        lambda Field, Model: Field(default=Model.DEFAULT_ELO)
    )

    @classmethod
    def get_game_model(cls):

        TPlayer = TypeVar('TPlayer', bound = Eloable)

        class GenericBase(Generic[TPlayer]):
            players: 'models.ManyToManyField[TPlayer, Any]'
            winner: 'models.ForeignKey[TPlayer]'

        class Game(models.Model, GenericBase[TPlayer]):

            class Meta:
                abstract = True

            players = models.ManyToManyField(cls.__name__, related_name='games')
            winner = models.ForeignKey(cls.__name__, related_name='games_won', on_delete=models.CASCADE)

        return Game[cls]

class TestPlayer(Eloable):
    DEFAULT_ELO = 1200.0

    name = models.CharField(max_length=255)

class TestGame(TestPlayer.get_game_model()):
    pass

    def __str__(self):
        return ' vs '.join(player.name for player in self.players.all())