import numpy as np
from time import time
from sklearn.cluster import KMeans
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer


evaluations = []
evaluations_std = []


def cluster_data(data: str, number_of_clusters: int = 10):
    """
    Runs the KMeans clustering algorithm on textual data to identify topics.
    :param data:
    :param number_of_clusters:
    :return:
    """
    vectorizer = TfidfVectorizer(
        max_df=0.5, # Ignore terms that appear in more than 50% of the documents
        min_df=5, # Ignore terms that are not present in at least 5 documents
        stop_words="english",
    )
    t0 = time()
    X_tfidf = vectorizer.fit_transform(data.split("\n"))

    print(f"vectorization done in {time() - t0:.3f} s")
    print(f"n_samples: {X_tfidf.shape[0]}, n_features: {X_tfidf.shape[1]}")
    print(f"Sparsity: {X_tfidf.nnz / np.prod(X_tfidf.shape):.3f}")

    for seed in range(5):
        kmeans = KMeans(
            algorithm='lloyd',
            n_clusters=number_of_clusters,
            max_iter=100,
            init='k-means++',
            n_init=1,
            random_state=seed,
        ).fit(X_tfidf)

        cluster_ids, cluster_sizes = np.unique(kmeans.labels_, return_counts=True)
        print(f"Number of elements assigned to each cluster: {cluster_sizes}")

        name = kmeans.__class__.__name__
        train_times = []
        scores = defaultdict(list)
        for s in range(5):
            kmeans.set_params(random_state=s)
            t0 = time()
            kmeans.fit(X_tfidf)
            train_times.append(time() - t0)
        train_times = np.asarray(train_times)

        print(f"clustering done in {train_times.mean():.2f} ± {train_times.std():.2f} s ")
        evaluation = {
            "estimator": name,
            "train_time": train_times.mean(),
        }
        evaluation_std = {
            "estimator": name,
            "train_time": train_times.std(),
        }

        for score_name, score_values in scores.items():
            mean_score, std_score = np.mean(score_values), np.std(score_values)
            print(f"{score_name}: {mean_score:.3f} ± {std_score:.3f}")
            evaluation[score_name] = mean_score
            evaluation_std[score_name] = std_score
        evaluations.append(evaluation)
        evaluations_std.append(evaluation_std)

        # Show results:
        original_space_centroids = kmeans.cluster_centers_
        order_centroids = original_space_centroids.argsort()[:, ::-1]
        terms = vectorizer.get_feature_names_out()

        for i in range(5):
            print(f"Cluster {i}: ", end="")
            for ind in order_centroids[i, :10]:
                print(f"{terms[ind]} ", end="")
            print()

