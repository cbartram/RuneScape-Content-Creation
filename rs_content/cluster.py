import numpy as np
from time import time
from sklearn import metrics
from sklearn.cluster import KMeans
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer


evaluations = []
evaluations_std = []


def vectorize_text(data: str):
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
    return X_tfidf, vectorizer


def k_means_cluster(vectors, true_k: int):
    for seed in range(5):
        kmeans = KMeans(
            n_clusters=true_k,
            max_iter=100,
            n_init=5,
            random_state=seed,
        ).fit(vectors)
        cluster_ids, cluster_sizes = np.unique(kmeans.labels_, return_counts=True)
        print(f"Number of elements asigned to each cluster: {cluster_sizes}")
    return kmeans


def fit_and_evaluate(km, X, name=None, n_runs=5):
    name = km.__class__.__name__ if name is None else name

    train_times = []
    scores = defaultdict(list)
    for seed in range(n_runs):
        km.set_params(random_state=seed)
        t0 = time()
        km.fit(X)
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
    return km