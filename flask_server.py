from http import HTTPStatus

from flask import Flask, jsonify, request
from flask_cors import CORS

from auth.decorators import get_user_from_request, login_required
from auth.jwt_handler import decode_jwt
from model.model import User, Actor, Show

app = Flask(__name__)
CORS(app)


@app.before_request
def prerequest():
    bearer_token = request.headers.get('Authorization', None)
    if bearer_token is None:
        return

    token_split = bearer_token.split(' ')
    if token_split[0] != 'Bearer':
        return

    token = token_split[1]
    payload = decode_jwt(token)
    if not payload:
        return

    user = User.get_user(payload['email'])
    request.user = user


@app.route('/signup', methods=['POST'])
def sign_up():
    data = request.get_json()
    if data is None:
        return jsonify({'error': "['email', 'password'] fields are required in body"}), HTTPStatus.BAD_REQUEST

    email = data.get("email", None)
    password = data.get("password", None)

    if None in [email, password]:
        return jsonify({'error': "['email', 'password'] fields are required in body"}), HTTPStatus.BAD_REQUEST

    try:
        user = User(email=email, password=password)
        user.create_user()
        return jsonify({'message': 'User registered successfully'})
    except Exception as exception:
        return jsonify({'error': str(exception)}), HTTPStatus.BAD_REQUEST


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if data is None:
        return jsonify({'error': "['email', 'password'] fields are required in body"}), HTTPStatus.BAD_REQUEST

    email = data.get("email", None)
    password = data.get("password", None)

    if None in [email, password]:
        return jsonify({'error': "['email', 'password'] fields are required in body"}), HTTPStatus.BAD_REQUEST

    try:
        user = User(email=email, password=password)
        token = user.login_user()
        return jsonify({'token': token})
    except Exception as exception:
        return jsonify({'error': str(exception)}), HTTPStatus.BAD_REQUEST


@app.route('/me', methods=['GET'])
@login_required
def me():
    user: User = get_user_from_request(request)
    return jsonify(user.get_object())


@app.route('/actor', methods=['GET'])
def get_actors():
    actors = Actor.get_all_data()
    return jsonify(actors)


@app.route('/actor', methods=['POST'])
def create_actor():
    data = request.get_json()

    if data is None:
        return jsonify({'error': "['name', 'photo'] fields are required in body"}), HTTPStatus.BAD_REQUEST

    name = data.get("name", None)
    photo = data.get("photo", None)

    if None in [name, photo]:
        return jsonify({'error': "['name', 'photo'] fields are required in body"}), HTTPStatus.BAD_REQUEST

    actor = Actor(name=name, photo=photo)
    actor.create_actor()

    return jsonify({'message': 'Actor created successfully'})


@app.route('/show', methods=['GET'])
def get_shows():
    actors = Show.get_all_data()
    return jsonify(actors)


@app.route('/show', methods=['POST'])
def create_show():
    data = request.get_json()

    if data is None:
        return jsonify({'error': "[title, release_year, episode_numbers, image, description, director, writer, genre, "
                                 "streaming_platform, actor_id] fields are required in body"}), HTTPStatus.BAD_REQUEST

    title = data.get("title", None)
    release_year = data.get("release_year", None)
    episode_numbers = data.get("episode_numbers", None)
    image = data.get("image", None)
    description = data.get("description", None)
    director = data.get("director", None)
    writer = data.get("writer", None)
    genre = data.get("genre", None)
    streaming_platform = data.get("streaming_platform", None)
    actor_id_list = data.get("actor_id_list", None)

    if None in [title, release_year, episode_numbers, image, description, director, writer, genre, streaming_platform, actor_id_list]:
        return jsonify({'error': "[title, release_year, episode_numbers, image, description, director, writer, genre, "
                                 "streaming_platform, actor_id_list] fields are required in body"}), HTTPStatus.BAD_REQUEST

    show = Show(title=title, release_year=release_year, episode_numbers=episode_numbers, image=image,
                description=description, director=director, writer=writer, genre=genre,
                streaming_platform=streaming_platform)
    for actor_id in actor_id_list:
        actor = Actor.get_actor(actor_id)

        if actor == {}:
            return jsonify({'error': 'Invalid actor id'}), HTTPStatus.BAD_REQUEST

        show.actors.append(actor)
    show.create_show()

    return jsonify({'message': 'Show created successfully'})


@app.route("/actor/<id>", methods=["DELETE"])
def delete_actor(id):
    try:
        Actor.delete_actor(id)
        return jsonify({'message': 'Record deleted successfully'})
    except Exception as exception:
        return jsonify({'error': str(exception)}), HTTPStatus.BAD_REQUEST


@app.route("/show/<id>", methods=["DELETE"])
def delete_show(id):
    try:
        Show.delete_show(id)
        return jsonify({'message': 'Record deleted successfully'})
    except Exception as exception:
        return jsonify({'error': str(exception)}), HTTPStatus.BAD_REQUEST


if __name__ == '__main__':
    app.run(host='localhost', port=8000, debug=True)
