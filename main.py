import os
import time
import json
import boto3
import smtplib
import pandas as pd
import requests as r
from logger import log
from datetime import date, datetime
from botocore.exceptions import ClientError


def fetch_reddit_posts(single_day: bool = True) -> int:
    """
    Fetches a series of Reddit posts for OldSchool RuneScape, processes them and writes them to files for
    future analysis.
    :param: single_day Boolean option to only pull data for a single day (based on the time this is running)
    :return:
    """
    today = date.today().strftime('%Y-%m-%d')
    log.info(f'---------------------- {today} ----------------------------')
    log.info(f"Running job at: {datetime.today().strftime('%Y-%m-%d %I:%M %p')}")
    log.info("Attempting to fetch Reddit Posts from api.pushshift.io")
    try:
        before_utc = int((datetime.utcnow() - datetime(1970, 1, 1)).total_seconds())
        after = before_utc - 86200
        single_day_option = "" if not single_day else f"&before={before_utc}&after={after}"
        res = r.get(f'https://api.pushshift.io/reddit/search/submission?size=500&subreddit=2007scape{single_day_option}')
        res.raise_for_status()
        data = res.json()
    except r.exceptions.HTTPError as errh:
        log.error(f'HTTP Error occurred while fetching Reddit posts from api.pushshift.io. Error = {str(errh)}')
        send_email()
        return 1
    except r.exceptions.ConnectionError as errc:
        log.error(f'Connection Error occurred while fetching Reddit posts from api.pushshift.io. Error = {str(errc)}')
        send_email()
        return 1
    except r.exceptions.Timeout as errt:
        log.error(f'Timeout Error occurred while fetching Reddit posts from api.pushshift.io. Error = {str(errt)}')
        send_email()
        return 1
    except r.exceptions.RequestException as err:
        log.error(
            f'General Request Exception thrown while fetching Reddit posts from api.pushshift.io. Error = {str(err)}')
        send_email()
        return 1

    reddit_posts = data['data']
    if len(reddit_posts) == 0:
        log.warn('No reddit posts were found for r/2007scape or an error occurred while fetching posts. '
                 'Nothing to process.')
        return 1
    else:
        log.info("Cleaning and condensing raw Reddit posts.")
        cleaned_posts = []
        for p in reddit_posts:
            cleaned_posts.append({
                'title': p['title'],
                'content': p['selftext'],
                'subreddit': p['subreddit'],
                'permalink': p['permalink'],
                'url': p['url'],
                'created_at_timestamp': time.strftime('%Y-%m-%d %I:%M %p', time.localtime(p['created_utc'])),
                'created_at_date': time.strftime('%Y-%m-%d', time.localtime(p['created_utc']))
            })

        log.info("Sorting and grouping Reddit posts by created date.")
        df = pd.DataFrame(cleaned_posts)
        df = df.sort_values(by='created_at_timestamp')
        grouped_reddit_posts = json.loads(df.groupby('created_at_date')
                                          .apply(lambda x: x.to_json(orient='records'))
                                          .to_json())

        log.info(f"Writing posts to file(s): {list(grouped_reddit_posts.keys())}")
        for k in grouped_reddit_posts.keys():
            file_path = os.path.join(os.getcwd(), 'data', f'osrs_reddit_{k}.json')
            with open(file_path, 'w') as f:
                f.write(grouped_reddit_posts[k])
            upload_file_s3(file_path, 'runescape-content-prod')

        log.info('Done.')
        return 0


def send_email():
    """
    Sends an email for monitoring purposes.
    """
    sender = os.getenv("LOGGING_EMAIL_SENDER", "test@mailtrap.io")
    receiver = os.getenv("LOGGING_EMAIL_RECEIVER", "test@mailtrap.io")
    today = date.today().strftime("%Y-%m-%d")
    log.info(f"Sending alert email to: {receiver}")

    # Read log output for today
    with open(f'logs/osrs_log_{today}.log', 'r') as log_file:
        log_data = log_file.read()

        message = f"""\
        Subject: RuneScape Redit -- Data Collection Failure 
    
        Hello we are just informing you that there was an error collecting data OSRS Reddit post data on: 
        {date.today().strftime('%Y-%m-%d')}.
        
        Log output:
        {log_data}
    
        Sincerely,
        
        The OSRS Content Team
        """
        with smtplib.SMTP("smtp.mailtrap.io", 25) as server:
            server.login(os.getenv("EMAIL_USERNAME", "user"), os.getenv("EMAIL_PASSWORD", "test1234"))
            server.sendmail(sender, receiver, message)
            log.info('Email sent.')
    log_file.close()


def upload_file_s3(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        log.info(f'File successfully uploaded to: s3://{bucket}/{object_name}')
        log.debug(response)
    except ClientError as e:
        log.error(e)
        return False
    return True


def run():
    """
    The Primary Entry point into the application
    :return:
    """
    fetch_reddit_posts()


if __name__ == '__main__':
    run()
