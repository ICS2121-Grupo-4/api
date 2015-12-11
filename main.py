#!/usr/local/bin python3
# -*- encoding: utf-8 -*-
from flask import Flask, request, jsonify, render_template
# import requests
import random as rnd
import numpy as np
import pickle
import os
import re
import parser

# Without trailing slash
MODELS_MATRIX_PATH = os.path.join(
    os.path.dirname(__file__), "../MODELS.matrix")
MOVIES_DAT_FILE = os.path.join(
    os.path.dirname(__file__), "../movies-dataset/ml-1m/movies.dat")


class API:
    def __init__(self, port, env):
        self.app = Flask(__name__)
        self.port = port
        self.env = env

        self.movies = parser.MoviesParser(MOVIES_DAT_FILE).parse()
        self.models = []

        self.app.jinja_env.add_extension("pyjade.ext.jinja.PyJadeExtension")

        self.load_models()

    def run(self):
        @self.app.route("/")
        def index():
            return render_template("index.jade")

        @self.app.route("/movie_info")
        def movie_info():
            movie_id = int(request.args.get("movie_id"))
            title = self.get_title_by_id(movie_id).title
            res = {}
            res["title"] = title
            res["image"] = self.get_movie_poster(title)
            res["movie_id"] = movie_id

            return jsonify(res)

        @self.app.route("/predict")
        def predict():
            # /predict?movies=100,200,100&ratings=5,3,2,3
            raw_movies = list(map(int, request.args.get("movies").split(",")))
            raw_ratings = map(int, request.args.get("ratings").split(","))
            # Vector de ceros.
            user_vector = np.zeros(self.NUM_MODELS)
            # Reemplazar valores del usuario en vector de ceros.
            for movie_id, rating in zip(raw_movies, raw_ratings):
                user_vector[movie_id - 1] = rating
            scores = self.models.dot(user_vector).T
            # Obtener mejores 5 puntajes.
            scores_sorted = sorted(
                list(enumerate(scores)),
                key=lambda s: s[1],
                reverse=True
            )
            results = scores_sorted[:4]
            res = {}
            for movie_id, score in results:
                movie_id = movie_id + 1
                title = self.get_title_by_id(movie_id).title
                res[movie_id] = {}
                res[movie_id]["title"] = title
                res[movie_id]["score"] = score.item(0)
                # TODO: Cache movie posters.
                res[movie_id]["image"] = self.get_movie_poster(title)

            return jsonify(res)

        @self.app.route("/random")
        def random():
            options = [1]
            choice = rnd.choice(options)
            title = self.get_title_by_id(choice).title
            res = {}
            res["title"] = title
            res["image"] = self.get_movie_poster(title)
            res["movie_id"] = choice

            return jsonify(res)

        debug = self.env == "DEV"
        self.app.run(port=self.port, debug=debug)

    def get_title_by_id(self, movie_id):
        try:
            return list(filter(
                lambda movie: movie.movie_id == movie_id,
                self.movies
            ))[0]
        except IndexError:
            print(movie_id)

    def get_movie_poster(self, title):
        # print(title)
        # req = requests.get(
            # "https://www.googleapis.com/customsearch/v1",
            # params={
                # "q": "{} movie poster".format(title),
                # "key": "AIzaSyCDGIyWsMsYBiwYFs6x4gxeqhXndemIGjQ",
                # "cx": "001335187956860902977:c_49g0yr6s8",
                # "searchType": "image"
            # }
        # )
        # print(req.json())

        # try:
            # return req.json()["items"][0]["link"]
        # except KeyError:
            # return "https://thetreasurehunteruk.files.wordpress.com/2011/10"
                    # "/rick-new2.jpg"
        return "https://thetreasurehunteruk.files.wordpress.com/2011/10" +\
               "/rick-new2.jpg"

    def load_models(self):
        with open(MODELS_MATRIX_PATH, "rb") as models_matrix_file:
            self.models = pickle.load(models_matrix_file)
        self.NUM_MODELS = np.shape(self.models)[0]


if __name__ == '__main__':
    port = int(os.getenv("PORT", default=1313))
    env = os.getenv("ENV", default="DEV")
    api = API(port, env)
    api.run()
