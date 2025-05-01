from typing import Any, Generic, TypeVar, cast

from utils.django import DynamicField
from utils.powerups.inheritance_protection import Uninheritable

from django.db import models


class PlayerBase(models.Model):

    class Meta:
        abstract = True

    DEFAULT_ELO = 1000.0
    K_FACTOR = 32.0
    DIVISOR = 400.0

    elo: 'models.FloatField[float]' = DynamicField(
        models.FloatField, lambda: PlayerBase,
        lambda Field, Model: Field(default=Model.DEFAULT_ELO)
    )

    @classmethod
    def base_game_model(cls):

        class TypedGame(GameBase[cls]):

            class Meta(GameBase.Meta):
                abstract = True

            override_inheritance_protection = True
            PlayerModel = cls
            between = models.ManyToManyField(cls, related_name='games')
            winner = models.ForeignKey(cls, 
                related_name='games_won', on_delete=models.CASCADE, null=True, blank=True
            )

        return cast(type[GameBase[cls]], TypedGame)

TPlayer = TypeVar('TPlayer', bound = PlayerBase)

class GameBase(models.Model, Generic[TPlayer], Uninheritable):

    class Meta:
        abstract = True

    intended_use = PlayerBase.base_game_model.__qualname__

    PlayerModel: type[TPlayer]
    between: 'models.ManyToManyField[TPlayer, Any]'
    winner: 'models.ForeignKey[TPlayer | None]'
    processed = models.BooleanField(default=False)

    def update_elos(self):
        from .methods import update_elos_after_game
        update_elos_after_game(self)

# class TestPlayer(PlayerBase):
#     DEFAULT_ELO = 1200.0

#     name = models.CharField(max_length=255)

# # class ErroneousGame(GameBase[TestPlayer]): # should raise TypeError
# #     pass

# class TestGame(TestPlayer.base_game_model()):
    
#     title = models.CharField(max_length=255, null=True, blank=True)

#     def __str__(self):
#         return self.title or ' vs '.join(player.name for player in self.between.all())