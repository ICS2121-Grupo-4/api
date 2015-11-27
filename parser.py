#!/usr/local/bin python3
# -*- encoding: utf-8 -*-


class Parser:
    def __init__(self, path):
        self.path = path


class RatingsParser(Parser):
    def parse(self):
        ratings = []
        with open(self.path) as ratings_file:
            for rating_line in ratings_file:
                ratings.append(Rating(*rating_line.strip().split("::")))
        return ratings


class Rating:
    def __init__(self, user_id, movie_id, rating, timestamp):
        self.user_id = int(user_id)
        self.movie_id = int(movie_id)
        self.rating = int(rating)
        self.timestamp = int(timestamp)


class UsersParser(Parser):
    def parse(self):
        users = []
        with open(self.path) as users_file:
            for user_line in users_file:
                users.append(User(*user_line.strip().split("::")))
        return users


class User:
    def __init__(self, user_id, gender, age, ocupation, zip_code):
        self.user_id = int(user_id)
        self.gender = gender
        self.age = int(age)
        self.ocupation = int(ocupation)
        self.zip_code = zip_code


class MoviesParser(Parser):
    def parse(self):
        movies = []
        with open(self.path, encoding="latin-1") as movies_file:
            for movie_line in movies_file:
                movies.append(Movie(*movie_line.strip().split("::")))
        return movies


class Movie:
    def __init__(self, movie_id, title, genres):
        self.movie_id = int(movie_id)
        self.title = title
        self.genre = genres
