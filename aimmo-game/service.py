#!/usr/bin/env python
import eventlet

eventlet.sleep()
eventlet.monkey_patch()

import cPickle as pickle
import logging
import os
import sys

import flask
from flask_socketio import SocketIO, emit

from simulation.turn_manager import state_provider
from simulation import map_generator
from simulation.avatar.avatar_manager import AvatarManager
from simulation.turn_manager import ConcurrentTurnManager
from simulation.worker_manager import WORKER_MANAGERS

app = flask.Flask(__name__)
socketio = SocketIO()

worker_manager = None

from connection.world_state import WorldState, BrowserWorldState, UnityWorldState

#setup the adaptors for the connection with the front-end
# world_state = BrowserWorldStat(state_provider)
world_state = UnityWorldState(state_provider)

@socketio.on('connect')
def world_update_on_connect():
    if isinstance(world_state, BrowserWorldState):
        emit(
            'world-update',
            world_state.get_init(),
        )
    elif isinstance(world_state, UnityWorldState):
        emit(
            'world-init',
            world_state.get_init(),
        )

def send_world_update():
    socketio.emit(
        'world-update',
        world_state.get_update(),
        broadcast=True,
    )

@app.route('/')
def healthcheck():
    return 'HEALTHY'

@app.route('/player/<player_id>')
def player_data(player_id):
    player_id = int(player_id)
    return flask.jsonify({
        'code': worker_manager.get_code(player_id),
        'options': {},       # Game options
        'state': None,
    })

def run_game(port):
    global worker_manager

    print("Running game...")
    settings = pickle.loads(os.environ['settings'])

    # TODO: this does not work with Kubernates; locally it works
    # as http://localhost:8000/players/api/games/ is used as default
    api_url = os.environ.get('GAME_API_URL', 'http://localhost:8000/players/api/games/')
    generator = getattr(map_generator, settings['GENERATOR'])(settings)
    player_manager = AvatarManager()
    game_state = generator.get_game_state(player_manager)

    turn_manager = ConcurrentTurnManager(game_state=game_state, end_turn_callback=send_world_update, completion_url=api_url+'complete/')
    WorkerManagerClass = WORKER_MANAGERS[os.environ.get('WORKER_MANAGER', 'local')]
    worker_manager = WorkerManagerClass(game_state=game_state, users_url=api_url, port=port)

    worker_manager.start()
    turn_manager.start()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    # We should set the resource right from the beginning or just not have it at all
    os.environ['SOCKETIO_RESOURCE'] = 'socket.io'
    socketio.init_app(app, resource=os.environ.get('SOCKETIO_RESOURCE', 'socket.io'))

    run_game(int(sys.argv[2]))

    # run the flusk persistent connection
    socketio.run(
        app,
        debug=False,
        host=sys.argv[1],
        port=int(sys.argv[2]),
        use_reloader=False,
    )
