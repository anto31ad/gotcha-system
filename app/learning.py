import csv
import numpy as np
import joblib

from pathlib import Path
from sklearn.cluster import KMeans

from .schema import Event
from . import paths

K_MEANS_PARAM = 3


def create_time_column(minutes_list: list[int]):
    minutes_norm = np.array(minutes_list) / 1440
    minutes_sin = np.sin(2 * np.pi * minutes_norm)
    minutes_cos = np.cos(2 * np.pi * minutes_norm)
    return np.column_stack([minutes_sin, minutes_cos])


def determine_optimal_number_of_cluster(
        data,
        min_clusters: int,
        max_clusters: int
):
    
    if min_clusters < 1 or max_clusters < 1:
        raise ValueError()
    elif min_clusters >= max_clusters:
        raise ValueError()

    # TECHNIQUE: elbow method
    # IDEA: try fitting kMeans with "data" with different k sizes, producing one model for each k:
    # the goal is to find the smallest k beyond which
    #   the decrease in inertia becomes small enough.

    # inertia (of a kmeans model) is the sum of the squared distances
    #   of each example E (of the training set) to the closest centroid
    # inertia_points will store the intertia of each model
    intertia_points = []
    for i in range(min_clusters, max_clusters):
        model = KMeans(
            n_clusters=i,
            # perform random restart n_init=5 times; then return the best cluster-set (in terms of intertia)
            n_init=5,      
            init='random',
        )
        model.fit(data)
        intertia_points.append(model.inertia_)


def train_user_models(event_examples: list[Event]):

    # check if there are at least two examples of events
    if len(event_examples) < 2:
        return

    # GOAL: Find patterns in the daily times each user interacts with the system. 

    # get the list of user appearing in the examples
    users_list =  sorted(set(e.user for e in event_examples))

    # Phase 2: train a model for each user
    user_models: dict[str, KMeans] = {}
    for user in users_list:
        model_filepath = paths.USER_MODELS_DIR / f"{user}.pkl"

        # get the minute examples for this user
        minutes = [e.time for e in event_examples if e.user == user]
        # check if there are at least K_MEANS_PARAM (number of clusters) examples for this user
        if len(minutes) < K_MEANS_PARAM:
            continue
        # build the column and train the model
        minutes_col = create_time_column(minutes)
        model = KMeans(n_clusters=K_MEANS_PARAM, random_state=0).fit(minutes_col)
        user_models[user] = model
        joblib.dump(model, model_filepath.resolve())
        print(f"Trained model for user '{user}''s daily time of activity")


def get_user_predictive_models():
    user_models: dict[str, KMeans] = {}

    # if models exist, load them
    for filepath in paths.USER_MODELS_DIR.glob("*.pkl"):
        username = filepath.name.split(".")[0]
        user_models[username] = joblib.load(filepath.resolve())

    return user_models


def check_event_using_predictor(user_models: dict, event: Event) -> list[str]:
    
    test_example = create_time_column([event.time])

    user_model = user_models.get(event.user)
    if not user_model:
        print(f"No model found for user {event.user}")
        return []

    distances = user_model.transform(test_example)[0]

    distances_norm = distances / distances.sum()
    print (f"{event.user}'s access time: {test_example[0]}")
    print(f"Distances from {event.user} at {event.time} to each cluster center: {distances}")
    print(f"Normalized distances (sum=1): {distances_norm}")
    print(f"Closest cluster: {np.argmin(distances)}")
    
    return []
