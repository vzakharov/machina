from typing import Any, Generic, TypeVar, cast

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
    def base_game_model(cls):

        class Game(GameBase[cls]):

            class Meta(GameBase.Meta):
                abstract = True

            PlayerModel = cls
            between = models.ManyToManyField(cls, related_name='games')
            winner = models.ForeignKey(cls, related_name='games_won', on_delete=models.CASCADE)

        return cast(type[GameBase[cls]], Game)

TPlayer = TypeVar('TPlayer', bound = Eloable)

class GameBase(models.Model, Generic[TPlayer]):

    class Meta:
        abstract = True

    PlayerModel: type[TPlayer]
    between: 'models.ManyToManyField[TPlayer, Any]'
    winner: 'models.ForeignKey[TPlayer]'

class TestPlayer(Eloable):
    DEFAULT_ELO = 1200.0

    name = models.CharField(max_length=255)

class TestGame(TestPlayer.base_game_model()):
    
    title = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.title or ' vs '.join(player.name for player in self.between.all())