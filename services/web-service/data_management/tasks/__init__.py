# Import all task modules to make them discoverable by Celery

# Player data tasks
from .player_tasks import (
    sync_player_data,
    sync_specific_players,
    sync_team_players,
    sync_popular_players,
    cleanup_player_data
)

# Make tasks available for import
__all__ = [
    # Player tasks
    'sync_player_data',
    'sync_specific_players', 
    'sync_team_players',
    'sync_popular_players',
    'cleanup_player_data',
]
