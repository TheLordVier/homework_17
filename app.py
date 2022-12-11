# app.py
# Импортируем фреймворк Flask и его функции
from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
# Импортируем библиотеку Marshmallow
from marshmallow import Schema, fields
# Импортируем модели из create_data.py, которые будем использовать
from create_data import Movie, Director, Genre

# Инициализируем приложение и настраиваем конфигурацию
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Описываем модель Movie в виде класса схемы
class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


# Описываем модель Director в виде класса схемы
class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


# Описываем модель Genre в виде класса схемы
class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


# Создаём класс Api в приложении
api = Api(app)
# Создаём неймпейсы для представлений
movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')

# Cоздаём экземпляры схем
movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


# Регистрируем класс (CBV) по эндпоинту указанному в movie_ns
@movie_ns.route("/")
class MoviesView(Resource):
# Получение списка всех сущностей
    def get(self):
        movies = db.session.query(Movie)
        director_id = request.args.get("director_id")
        if director_id is not None:
            movies = movies.filter(Movie.director_id == director_id)
        genre_id = request.args.get("genre_id")
        if genre_id is not None:
            movies = movies.filter(Movie.genre_id == genre_id)
        return movies_schema.dump(movies.all()), 200

# Создание определённой сущности
    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return "Movie created", 201


# Регистрируем класс (CBV) по эндпоинту указанному в movie_ns
@movie_ns.route("/<int:mid>")
class MovieView(Resource):
# Получение конкретной сущности по идентификатору
    def get(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return "Movie not found", 404
        return movie_schema.dump(movie), 200

# Обновление конкретной сущности по идентификатору
    def put(self, mid: int):
        updated_movie = db.session.query(Movie).filter(Movie.id == mid).update(request.json)
        if updated_movie != 1:
            return "Not updated", 400
        db.session.commit()
        return "Movie updated", 204

# Удаление конкретной сущности по идентификатору
    def delete(self, mid: int):
        movie = db.session.query(Movie).get(mid)
        if not movie:
            return "Movie not found", 400
        db.session.delete(movie)
        db.session.commit()
        return "Movie deleted", 204


# Регистрируем класс (СBV) по эндпоинту указанному в director_ns
@director_ns.route("/")
class DirectorsView(Resource):
# Получение списка всех сущностей
    def get(self):
        directors = db.session.query(Director)
        return directors_schema.dump(directors), 200

# Создание определённой сущности
    def post(self):
        req_json = request.json
        new_director = Director(**req_json)
        with db.session.begin():
            db.session.add(new_director)
        return "Director created", 201


# Регистрируем класс (СBV) по эндпоинту указанному в director_ns
@director_ns.route("/<int:did>")
class DirectorView(Resource):
# Получение конкретной сущности по идентификатору
    def get(self, did: int):
        try:
            director = db.session.query(Director).get(did)
            return director_schema.dump(director), 200
        except Exception:
            return str(Exception), 404

# Обновление конкретной сущности по идентификатору
    def put(self, did: int):
        req_json = request.json
        director = db.session.query(Director).get(did)
        if "name" in req_json:
            director.name = req_json.get("name")
        db.session.add(director)
        db.session.commit()
        return "Director updated", 204

# Удаление конкретной сущности по идентификатору
    def delete(self, did: int):
        director = db.session.query(Director).get(did)
        if not director:
            return "Director not found", 400
        db.session.delete(director)
        db.session.commit()
        return "Director deleted", 204


# Регистрируем класс (CBV) по эндпоинту указанному в genre_ns
@genre_ns.route("/")
class GenresView(Resource):
# Получение списка всех сущностей
    def get(self):
        genres = db.session.query(Genre)
        return genres_schema.dump(genres), 200

# Создание определённой сущности
    def post(self):
        req_json = request.json
        new_genre = Genre(**req_json)
        with db.session.begin():
            db.session.add(new_genre)
        return "Genre created", 201


# Регистрируем класс (CBV) по эндпоинту указанному в genre_ns
@genre_ns.route("/<int:gid>")
class GenreView(Resource):
# Получение конкретной сущности по идентификатору
    def get(self, gid: int):
        try:
            genre = db.session.query(Genre).get(gid)
            return genre_schema.dump(genre), 200
        except Exception:
            return str(Exception), 404

# Обновление конкретной сущности по идентификатору
    def put(self, gid: int):
        genre = db.session.query(Genre).get(gid)
        req_json = request.json
        if "name" in req_json:
            genre.name = req_json.get("name")
        db.session.add(genre)
        db.session.commit()
        return "Genre updated", 204

# Удаление конкретной сущности по идентификатору
    def delete(self, gid: int):
        genre = db.session.query(Genre).get(gid)
        if not genre:
            return "Genre not found", 400
        db.session.delete(genre)
        db.session.commit()
        return "Genre deleted", 204


if __name__ == '__main__':
    app.run(debug=True)
