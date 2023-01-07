import json
import boto3
import numpy as np
from sklearn.datasets import fetch_20newsgroups


def load_from_s3(bucket: str):
    data = ""
    # Content in a reddit post which should be removed from analysis and clustering.
    # Things like [removed], &amp;#x200B;, URL's, blank strings, etc... TODO this may make for a good configuration parameter later on.
    # This will completely OMIT the content. We will strip the content of this stuff later on if it is present along
    # with other good information/text
    omitted_content = ['[removed]']

    client = boto3.client('s3')

    # List objects
    object_keys = []
    response = client.list_objects_v2(Bucket=bucket)
    object_keys = [obj['Key'] for obj in response['Contents']]

    # Get data for each Object
    for key in object_keys:
        r = client.get_object(Bucket=bucket, Key=key)
        contents = r['Body'].read()
        reddit_posts = json.loads(contents.decode("utf-8"))
        for reddit_post in reddit_posts:
            data += reddit_post['title']
            print(reddit_post['content'] + "\n")
            if reddit_post['content'] not in omitted_content and len(reddit_post['content']) > 0:
                pass





def run():
    categories = [
        "alt.atheism",
        "talk.religion.misc",
        "comp.graphics",
        "sci.space",
    ]

    dataset = fetch_20newsgroups(
        remove=("headers", "footers", "quotes"),
        subset="all",
        categories=categories,
        shuffle=True,
        random_state=42,
    )
    print(dataset)

    labels = dataset.target
    print("Target labels: ", dataset.target)
    unique_labels, category_sizes = np.unique(labels, return_counts=True)
    print("Unique labels and cat sizes: ", unique_labels, category_sizes)
    true_k = unique_labels.shape[0]

    print(f"{len(dataset.data)} documents - {true_k} categories")

