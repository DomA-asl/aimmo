from django.shortcuts import render
from players import app_settings


def render_game(request, game):
    """
    :param request: Request object used to generate this response.
    :param game: Game object.
    :return: HttpResponse object with a given context dictionary and a template.
    """
    context = {'current_user_player_key': request.user.pk, 'active': game.is_active,
               'static_data': game.static_data or '{}'
               }

    connection_settings = get_environment_connection_settings(request, game.id)

    context.update(connection_settings)

    return render(request, 'players/viewer.html', context)


def get_environment_connection_settings(request, game_id):
    """
    This function will return the correct URL parts and a SSL flag
    based on the environment of which it exists in.

    :param request: Request object used to generate this response.
    :param game_id: Integer with the ID of the game.
    :return: A dict object with all relevant settings.
    """
    # TODO: consider removing web_host_base if it's not used?

    return {
        'game_url_base': app_settings.GAME_SERVER_URL_FUNCTION(game_id)[0],
        'game_url_path': app_settings.GAME_SERVER_URL_FUNCTION(game_id)[1],
        'game_url_port': app_settings.GAME_SERVER_PORT_FUNCTION(game_id),
        'game_ssl_flag': app_settings.GAME_SERVER_SSL_FLAG, 'game_id': game_id,
        'web_host_base': request.get_host()
    }