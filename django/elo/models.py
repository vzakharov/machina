from typing import Any, TypeVar

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

TEloableModel = TypeVar('TEloableModel', bound = type[Eloable])

def GameModel(PlayerModel: TEloableModel): # pyright: ignore[reportInvalidTypeVarUse]

    class GameModel(models.Model):

        class Meta:
            abstract = True

        players: 'models.ManyToManyField[TEloableModel, Any]' = ( # pyright: ignore[reportInvalidTypeArguments]
            models.ManyToManyField(PlayerModel.__name__, related_name='games') 
        )
        winner: 'models.ForeignKey[TEloableModel]' = ( # pyright: ignore[reportInvalidTypeArguments]
            models.ForeignKey(PlayerModel.__name__, related_name='games_won', on_delete=models.CASCADE)
        )

    return GameModel

class TestGame(GameModel(TestPlayer)):
    
    def __str__(self) -> str:
        return f'{self.players.first()} vs {self.players.last()}'
