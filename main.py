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
MODELS_FOLDER = os.path.join(os.path.dirname(__file__), "../models")
MOVIES_DAT_FILE = os.path.join(
    os.path.dirname(__file__), "../movies-dataset/ml-1m/movies.dat")


class API:
    def __init__(self, port):
        self.app = Flask(__name__)
        self.port = port

        self.movies = parser.MoviesParser(MOVIES_DAT_FILE).parse()
        self.models = []

        self.app.jinja_env.add_extension("pyjade.ext.jinja.PyJadeExtension")

        self.calculate_model_dimensions()
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
            user_vector = np.zeros(self.NUM_ENTRIES + 1)
            # Reemplazar valores del usuario en vector de ceros.
            for movie_id, rating in zip(raw_movies, raw_ratings):
                user_vector[movie_id - 1] = rating
            scores = {}
            # Calcular predicción para todas las películas (descartando las
            # evaluadas).
            models_to_evaluate = [model_id for model_id in self.models
                                  if model_id not in raw_movies]
            for model_id in models_to_evaluate:
                with open(
                    "{}/{}.model".format(MODELS_FOLDER, model_id - 1),
                    "rb"
                ) as model_file:
                    model = pickle.load(model_file)

                # Borrar componente de la película que se va a evaluar.
                particular_user_vector = np.delete(
                    user_vector,
                    model_id - 1,
                    axis=0
                )
                scores[model_id] = model.coef_.T.dot(particular_user_vector)
            # Obtener mejores 5 puntajes.
            scores_sorted = sorted(
                list(scores.items()),
                key=lambda s: s[1],
                reverse=True
            )
            results = scores_sorted[:4]
            res = {}
            for movie_id, score in results:
                title = self.get_title_by_id(movie_id).title
                res[movie_id] = {}
                res[movie_id]["title"] = title
                res[movie_id]["score"] = score
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

        self.app.run(port=self.port, debug=True)

    def get_title_by_id(self, movie_id):
        return list(filter(
            lambda movie: movie.movie_id == movie_id,
            self.movies
        ))[0]

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

    def calculate_model_dimensions(self):
        # Number of entries per vector
        # TODO: Loop infinito si es que no existen modelos.
        model_id = 0
        not_finished = True
        while not_finished:
            filename = "{}/{}.model".format(MODELS_FOLDER, model_id)
            try:
                with open(filename, "rb") as model_file:
                    model = pickle.load(model_file)
                    self.NUM_ENTRIES = len(model.coef_)
                    not_finished = False
            except FileNotFoundError:
                model_id += 1
        # Number of models
        models_files_unfiltered = os.listdir(MODELS_FOLDER)
        models_files = list(filter(
            lambda p: re.match(".*\.model$", p),
            models_files_unfiltered
        ))
        self.MAX_MODEL_ID = max(map(
            lambda p: int(p.split(".")[0]),
            models_files
        ))
        self.NUM_MODELS = len(list(models_files))

    def load_models(self):
        for model_id in range(self.MAX_MODEL_ID):
            try:
                filename = "{}/{}.model".format(MODELS_FOLDER, model_id)
                if os.path.isfile(filename):
                    self.models.append(model_id + 1)
            except FileNotFoundError:
                pass


if __name__ == '__main__':
    api = API(1313)
    api.run()
