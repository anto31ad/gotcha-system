import numpy as np
import joblib
import matplotlib.pyplot as plt

from pathlib import Path
from kneed import KneeLocator
from sklearn.cluster import KMeans

from .schema import Event
from . import paths

KMEANS_MAX_K = 10
KMEANS_RANDOM_RESTARTS = 5

def create_time_column(minutes_list: list[int]):
    minutes_norm = np.array(minutes_list) / 1440
    minutes_sin = np.sin(2 * np.pi * minutes_norm)
    minutes_cos = np.cos(2 * np.pi * minutes_norm)
    return np.column_stack([minutes_sin, minutes_cos])


def calculate_optimal_k_for_kmeans(
        data,
        min_clusters: int,
        max_clusters: int,
        plot_path: Path | None = None,
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
    
    range_k = range(min_clusters, max_clusters)
    for i in range_k:
        model = KMeans(
            n_clusters=i,
            # perform random restart n_init=5 times; then return the best cluster-set (in terms of intertia)
            n_init=KMEANS_RANDOM_RESTARTS,      
            init='random',
        )
        model.fit(data)
        intertia_points.append(model.inertia_)

    kneeloc = KneeLocator(
        x=range_k,
        y=intertia_points,
        curve='convex',         # convex to detect elbows
        direction='decreasing', # intertia decreases as k grows
    )

    # write the plot to file, for debugging
    if plot_path:
        plt.figure()
        plt.plot(list(range_k), intertia_points, 'bo-')
        if kneeloc.elbow is not None:
            plt.vlines(
                kneeloc.elbow,
                plt.ylim()[0],
                plt.ylim()[1],
                linestyles='dashed',
                colors='red')
        plt.xlabel('Number of clusters (k)')
        plt.ylabel('Inertia')
        plt.title('Optimizing k using the Elbow Method')
        plt.savefig(plot_path.resolve())
        plt.close()

    return kneeloc.elbow


def train_user_models(event_examples: list[Event]):
    # GOAL: Find patterns in the daily times each user interacts with the system. 

    # check if there are at least two examples of events
    if len(event_examples) < 2:
        return

    # get the list of user appearing in the examples and train a model for each one
    users_list =  sorted(set(e.user for e in event_examples))
    for user in users_list:
        model_filepath = paths.USER_MODELS_DIR / f"{user}.pkl"
        model_optimal_k_plot_filepath = paths.USER_MODELS_DIR / f"{user}_elbow.png"

        # get the minute examples for this user
        minutes = [e.time for e in event_examples if e.user == user]
        # check if there are at least KMEANS_MAX_K (number o10 clusters) examples for this user
        if len(minutes) < KMEANS_MAX_K:
            print(f"(!) Could not train model for user '{user}': "
                  f"At least {KMEANS_MAX_K} examples are needed, but just {len(minutes)} were provided")
            continue
        # build the column and train the model
        minutes_col = create_time_column(minutes)
        optimal_k = calculate_optimal_k_for_kmeans(
            data=minutes_col,
            min_clusters=1,
            max_clusters=KMEANS_MAX_K,
            plot_path=model_optimal_k_plot_filepath
        )

        if not optimal_k:
            print(f"(!) Could not train model for user '{user}': "
                  "no optimal parameters found")
            continue

        model = KMeans(
            n_clusters=optimal_k,
            n_init=KMEANS_RANDOM_RESTARTS,
            init='random',
            random_state=42
        )
        model.fit(minutes_col)
    
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

    # the idea is to compute the distance of the event from the closest centroid
    distances = user_model.transform(test_example)[0]
    min_distance = np.min(distances)
    percentage = (min_distance / 2)

    if percentage < 0.25:
        return []

    return [f"Distance to closest centroid: {min_distance:.4f} ({percentage:.2f}% of max possible)"]
