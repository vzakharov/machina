from elo.models import Game, TPlayer

from django.db import transaction


def get_win_probability(player: TPlayer, *all_players: TPlayer):
    average_elo = sum(opponent.elo for opponent in all_players if opponent != player) / (len(all_players) - 1)
    # We don't actually expect there to be more than 2 players in a game, but it doesn't hurt to support more
    return 1.0 / ( 1.0 + 10 ** ((average_elo - player.elo) / type(player).DIVISOR) )

def update_elos_after_game(game: Game[TPlayer]):
    if game.processed:
        raise ValueError(f'{game} is already processed')
    winner = game.winner
    players = list(game.between.all())
    if winner and winner not in players:
        raise ValueError(f'{winner=} for {game} is not among {players}')
    if len(players) < 2:
        raise ValueError(f'{game} has less than 2 players: {players}')
    with transaction.atomic():
        for player, delta in calculate_deltas(players, winner):
            player.elo += delta
            player.save()
        game.processed = True
        game.save()

def calculate_deltas(players: list[TPlayer], winner: TPlayer | None):
    return {
        player: (
            type(players[0]).K_FACTOR 
            * (
                ( int(player == winner) if winner else 0.5 )
                - get_win_probability(player, *players)
            )
        )
        for player in players
    }.items()
