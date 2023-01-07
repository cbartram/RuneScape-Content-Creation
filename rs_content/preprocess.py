import re
import json
import boto3
import numpy as np
from sklearn.datasets import fetch_20newsgroups


def load_data_from_s3(bucket: str):
    """
    Reads all data files in the root of an S3 bucket and returns the text as a new line delimited string
    :param bucket: String the S3 bucket to read data from
    :return: String representing both the titles and content of each individual reddit post
    """
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
            data += reddit_post['title'] + "\n"
            if reddit_post['content'] not in omitted_content and len(reddit_post['content']) > 0:
                data += reddit_post['content'] + "\n"
    return data


def clean_data(data: str) -> str:
    cleaned = ""
    regexes = [
        r"\[.+?\]\(.+?\)", #Markdown links
        r"((?<=[^a-zA-Z0-9])(?:https?\:\/\/|[a-zA-Z0-9]{1,}\.{1}|\b)(?:\w{1,}\.{1}){1,5}(?:"
                                    "com|org|edu|gov|uk|net|ca|de|jp|fr|au|us|ru|ch|it|nl|se|no|es|mil|iq|io|ac|ly|sm)"
                                    "{1}(?:\/[a-zA-Z0-9]{1,})*)", # URL's
        r"&amp;#x200B;{1,}",
        r"&amp;{1,}",
        r"\\-",
        r"\*\*",
        r"\*",
        r"\/",
        r"&gt;{1,}",
        r"TL;DR{1,}"
    ]
    for line in data.split("\n"):
        if len(line) > 0:
            # Match markdown URL's and standard URL's
            for regex in regexes:
                m = re.finditer(regex, line, re.MULTILINE)
                for matchNum, match in enumerate(m, start=1):
                    # TODO Doesnt work for 2 links on the same line i.e "hey [how](are) you doing [today](okay)."
                    line = line[0:match.start()] + line[match.end()::]
                    # After trimming out the URL from the content sometimes the content is now blank so omit it
                    if len(line.strip()) == 0:
                        continue

            # There is a specific instance of url's which look like https://.png?.... which need to be manually parsed
            # as the regex doesn't catch them. The line can just be deleted since i've only seen instances where its
            # the url as the only content in the line
            if "https://.png?" in line:
                continue
        cleaned += line + "\n"
    return cleaned

