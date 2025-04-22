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

class TestPlayer(Eloable):
    DEFAULT_ELO = 1200.0

TPlayer = TypeVar('TPlayer', bound = Eloable)

def GameAmong(PlayerModel: type[TPlayer]): # pyright: ignore[reportInvalidTypeVarUse]

    P = TypeVar('P', bound = Eloable)

    class GenericBase(Generic[P]):
        players: 'models.ManyToManyField[P, Any]'
        winner: 'models.ForeignKey[P]'

    class GameAmong(models.Model, GenericBase[P]):

        class Meta:
            abstract = True

        players = models.ManyToManyField(PlayerModel.__name__, related_name='games') 
        winner = models.ForeignKey(PlayerModel.__name__, related_name='games_won', on_delete=models.CASCADE)

    return GameAmong[TPlayer]

class TestGame(GameAmong(TestPlayer)):
    
    def get_players(self):
        return list(self.players.all())