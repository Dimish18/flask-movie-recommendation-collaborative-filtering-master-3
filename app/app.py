import pandas as pd
from scipy import sparse
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify , render_template , flash
from recommend_manager import MovieManager
import json
import re
import requests
import ssl
import warnings

warnings.filterwarnings("ignore")  # ignore warnings

movieManager = MovieManager()
app = Flask(__name__)
app.config.update(
    TESTING = True,
    SECRET_KEY = "password"
)

# ------------------------------- FLASK ROUTES ------------------------------- #


@app.route("/" , methods=["POST" , "GET"])
def home():
    error = False
    error_message = ""
    movie_list =  movieManager.get_movie_list()

    try:
        if request.method == "POST":
            movie_form_input = request.form["movie_input"]
            try:
                rating_form_input = int(request.form["rating_input"])
            except Exception as e:
                print("EXCEPTION: at rating_form_input")


            if movie_form_input and rating_form_input:
                movieManager.add_movie([movie_form_input , rating_form_input])
                flash(f"Successfully added [{movie_form_input}]" , "info")
            else:
                error = True
                error_message = "Movie Input box Empty"
                print("No movie Added , Detected Empty form")


            print(f"{movie_form_input} added")
    except Exception as e:
        print(f"EXCEPTION AT HOME: {e}")
        print("MOVIE NOT IN DB")

    return render_template("index.html" , error = error , error_msg = error_message , movie_list = json.dumps(movie_list))


@app.route("/get_recommend", methods=["POST"])
def get_recommendation():
    recommended_movies = movieManager.getRecommendations(movieManager.get_watched_movie())

    movieManager.clear_movie_index()
    movieManager.get_all_movies_index(recommended_movies)
    reco_movies_index_list = movieManager.recommended_movies_index

    

    # reco_movies_index
    print("----------------")
    print(recommended_movies)
    print("----------------")
    print(reco_movies_index_list) 

    m0 = [re.sub(r" *\([^)]*\) *", '', i) for i in recommended_movies]
    m1 = [re.sub(r'[^\w\s\']|_', '', i) for i in m0]
    m2 = [re.sub(r'\s+', '+', i) for i in m1]
    # m3 = [re.sub(" ", "+", i) for i in m2]

    # print(reco_movies_dict)
    movie_images = []

    for movie in m2:
        response = requests.get("https://api.themoviedb.org/3/search/movie?api_key=45f8ee72b4c92bcc86d6559e4eaf7c5d&query=" + movie , verify = False )
        result = response.json()['results']
        if len(result) > 0:
            movie_images.append("https://image.tmdb.org/t/p/original/" + result[0]["poster_path"])
        else:
            movie_images.append("static/img/not_found.png")

    print(movie_images)
    
    reco_movies_dict = dict(zip(recommended_movies , movie_images))

    # return jsonify('',render_template('dynamic_movies.html', MOVIE_DATA = reco_movies_dict))
    return jsonify('',render_template('dynamic_movies.html', MOVIE_DATA = reco_movies_dict))

@app.route("/display_recommendation")
def display_recommendation():
    '''
        when get_recommendation is clicked
            display all recommended movies
    '''
    pass

@app.route("/clear_movies" , methods=["POST" , "GET"])
def clear_existing_movies():
    movieManager.clear_movie()
    log_message = "Movies Cleared"
    print("Movies Cleared")

    return jsonify('',render_template('dynamic_movies.html' , LOG = log_message))

if __name__ == '__main__':
    app.run(debug = True)

# ,verify='C:\movie recomm\flask-movie-recommendation-collaborative-filtering-master-3\chain.pem'