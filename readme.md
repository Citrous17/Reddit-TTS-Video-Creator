# Reddit TTS Video Generator

This program uses the Reddit API to retrieve a specified number of posts from a chosen subreddit, converts the text from each post to speech using Google Cloud's Text-to-Speech API, and overlays the speech onto a video background. Finally, the video is uploaded to Google Drive.

## Setup

To use this program, you'll need to do the following:

1. Install the required packages by running `pip install -r requirements.txt`.
2. Create a Reddit app on the Reddit website to obtain a CLIENT_ID and a SECRET_TOKEN. See Reddit's documentation for more information.
3. Enable the Google Drive API and create credentials for the application. Save the `credentials.json` file to the project directory.
4. Create a new project in the Google Cloud Console and enable the Text-to-Speech API. Download the service account key and save it to the project directory.
5. Rename the JSON key file to client_secret.json and move it to the root of the project.
6. Set the appropriate values for the constants in `main.py`.
7. Run `main.py` to generate the videos and upload them to Google Drive.

## Constants

- `NUM_VIDEOS`: The number of videos to generate.
- `SUBREDDIT`: The subreddit to pull posts from.
- `RANDOMSUBREDDIT`: Whether to choose a random subreddit from `SubredditsAndFolders`.
- `BACKGROUND`: The path to the video background.

## SubredditsAndFolders

A dictionary that maps subreddit names to Google Drive folder IDs. Update this dictionary to include new subreddits and their corresponding folder IDs.

## Text Manipulation

The program performs some basic text manipulation on the post titles and selftexts to remove profanity and replace certain phrases. It also performs a check to ensure that the post does not violate community guidelines before proceeding.

## Acknowledgments

This program was created by Citrous17 and is licensed under the MIT license.
