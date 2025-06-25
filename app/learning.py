import numpy as np
import joblib
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

from pathlib import Path
from kneed import KneeLocator
from sklearn.cluster import KMeans

from .utils import sincos_to_minutes, minutes_to_hhmm
from .schema import Event
from . import paths

KMEANS_MAX_K = 10
KMEANS_RANDOM_RESTARTS = 5
NORMAL_ACCESS_TIME_THRESHOLD_MINUTES = 120

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
    inertia_points = []
    
    range_k = range(min_clusters, max_clusters)
    for i in range_k:
        model = KMeans(
            n_clusters=i,
            # perform random restart n_init=5 times; then return the best cluster-set (in terms of intertia)
            n_init=KMEANS_RANDOM_RESTARTS,      
            init='random',
        )
        model.fit(data)
        inertia_points.append(model.inertia_)

    kneeloc = KneeLocator(
        x=range_k,
        y=inertia_points,
        curve='convex',         # convex to detect elbows
        direction='decreasing', # intertia decreases as k grows
    )

    # plot the curve and write the plot to file (for debugging)
    if plot_path:
        plt.figure()
        plt.plot(list(range_k), inertia_points, 'bo-')
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

def _plot_user_clusters(
        user_model: KMeans, # fitted kmeans model
        examples,   # numpy column
        user: str,
        plot_filepath: Path,
):

    centroids = user_model.cluster_centers_

    plt.figure(figsize=(6, 6))
    
    # plot the examples with blue bullets
    plt.scatter(examples[:, 0], examples[:, 1], c='blue', label='Examples', alpha=0.6)
    # plot the centroids with a red X
    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='X', s=200, label='Centroids')

    # draw the unit circle for reference
    circle = Circle((0, 0), 1, color='gray', fill=False, linestyle='--', alpha=0.5)
    plt.gca().add_artist(circle)

    for hour in range(24):
        angle = 2 * np.pi * (hour / 24)
        x_outer = 0.95 * np.sin(angle)
        y_outer = 0.95 * np.cos(angle)
        x_inner = 0.92 * x_outer
        y_inner = 0.92 * y_outer
        plt.plot(
            [x_inner, x_outer],
            [y_inner, y_outer], color='gray', lw=2)
        # Label main hours
        if hour % 6 == 0:
            label = str(hour)
            x_label = 0.7 * x_outer
            y_label = 0.7 * y_outer
            plt.text(x_label, y_label, label, ha='center', va='center', fontsize=10, fontweight='bold')

    plt.xlabel('sin(time)')
    plt.ylabel('cos(time)')
    plt.title(f'User {user} - Daily time of activity')
    plt.legend()

    plt.axis('equal')
    plt.grid(True)
    plt.savefig(plot_filepath.resolve())
    plt.close()


def learn_users_time_patterns(event_examples: list[Event]):
    # GOAL: Find patterns in the daily times each user interacts with the system. 

    # check if there are at least two examples of events
    if len(event_examples) < 2:
        return

    # get the list of user appearing in the examples and train a model for each one
    users_list =  sorted(set(e.user for e in event_examples))
    for user in users_list:
        model_filepath = paths.PREDICTORS_DIR / f"{user}.pkl"
        model_optimal_k_plot_filepath = paths.PREDICTOR_PLOTS_DIR / f"{user}_elbow.png"
        clusters_plot_filepath = paths.PREDICTOR_PLOTS_DIR / f"{user}_clusters.png"

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

        # plot the clusters (for debugging)
        _plot_user_clusters(
            model,
            minutes_col,
            user,
            clusters_plot_filepath)


        joblib.dump(model, model_filepath.resolve())
        print(f"Trained model for user '{user}''s daily time of activity")


def get_user_predictors() -> dict[str, KMeans]:
    user_models: dict[str, KMeans] = {}

    # if models exist, load them
    for filepath in paths.PREDICTORS_DIR.glob("*.pkl"):
        username = filepath.name.split(".")[0]
        user_models[username] = joblib.load(filepath.resolve())

    return user_models


def check_event_using_predictor(user_predictors: dict[str, KMeans], event: Event) -> list[str]:
    
    user_model: KMeans | None = user_predictors.get(event.user)
    if user_model is None:
        return []

    test_example = create_time_column([event.time])

    # the idea is to compute the distance of the event from the closest centroid
    distances = user_model.transform(test_example)[0]
    closest_cluster_id = np.argmin(distances)
    closest_centroid = user_model.cluster_centers_[closest_cluster_id]
    sin_val, cos_val = closest_centroid[0], closest_centroid[1]
    centroid_in_minutes = sincos_to_minutes(sin_val, cos_val)

    # get the time difference (in minutes) between centroid and the event time
    diff = abs(centroid_in_minutes - event.time)
    # handle wrap-around:
    #   ex. the difference between 0 and 60 (1AM) is 60 m.
    #   the difference between 0 and 1380 (11PM) should be 60m,
    #    but without the following wrap, it would be 1380m (11 hours), wrongly. 
    diff = min(diff, 1440 - diff)

    # if time difference is within the agreed "normal" threshold, return no anomaly
    if diff <= NORMAL_ACCESS_TIME_THRESHOLD_MINUTES:
        return []
    # ...otherwise...
    return [f"time of activity is {diff} minutes off the"
            f" closest average time of activity for user '{event.user}'"
            f" ({minutes_to_hhmm(centroid_in_minutes)})"]
