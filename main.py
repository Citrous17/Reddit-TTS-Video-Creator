from __future__ import print_function
import requests
from google.cloud import texttospeech
from moviepy.editor import *
import random
import os.path
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from tqdm import tqdm

#Customize request
NUM_VIDEOS = 3
SUBREDDIT = "AmItheAsshole" #nuclearrevenge, pettyrevenge, AmItheAsshole, nosleep, AskReddit

RANDOMSUBREDDIT = False

BACKGROUND = "insert_video_path_here"

# note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
print("Contacting Reddit...")

SubredditsAndFolders = {
    "nuclearrevenge": "GoogleDriveID",
    "pettyrevenge": "GoogleDriveID",
    "AmItheAsshole": "GoogleDriveID",
    "nosleep" : "GoogleDriveID",
}
if(RANDOMSUBREDDIT):
    SUBREDDIT = random.choice(SubredditsAndFolders.keys())
auth = requests.auth.HTTPBasicAuth('CLIENT_ID', 'SECRET_TOKEN')

# here we pass our login method (password), username, and password
data = {'grant_type': 'password',
        'username': 'your_reddit_username',
        'password': 'your_reddit_password'}

# setup our header info, which gives reddit a brief description of our app
headers = {'User-Agent': 'Python.bot_name.bot_version'}

# send our request for an OAuth token
res = requests.post('https://www.reddit.com/api/v1/access_token',
                    auth=auth, data=data, headers=headers)

# convert response to JSON and pull access_token value
TOKEN = res.json()['access_token']

# add authorization to our headers dictionary
headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

# while the token is valid (~2 hours) we just add headers=headers to our requests
requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)

res = requests.get("https://oauth.reddit.com/r/" + SUBREDDIT + "/hot?limit=10",
                   headers=headers)

print("Done Contacting!")

def utf8len(s):
    return len(s.encode('utf-8'))

count = 3
for post in res.json()['data']['children']:
    match SUBREDDIT:
        case "nuclearrevenge":
            text = "Welcome back to another episode of Nuclear Revenge. Today's story is titled: "
        case "pettyrevenge":
            text = "Welcome back to another episode of Petty Revenge. Today's story is titled: "
        case "AmItheAsshole":
            text = "Welcome back to another episode of Am I the BLEEP. Today's story is titled: "
        case "AskReddit":
            text = "Welcome back to another episode of Ask Reddit. Today's story is titled: "
        case _:
            text = "Welcome back to another episode of " + SUBREDDIT + ". Today's story is titled: "
        
    text = post['data']['title']
    id = post['data']['id']
 
    with open("videoIDs.txt", "r+") as f:
        if id in f.read():
            continue
        else:
            f.write(id)
            f.write("\n")

    if(count < 2):
        count+=1
        continue

    if(count - 2 > NUM_VIDEOS):
        print('\a')
        break

    print("Post " + str(count - 2) + " of " + str(NUM_VIDEOS) + "...")

    text += " " + post['data']['selftext']
    text += "Credit to user " + str(post['data']['author'] + " for this post.")

    text = text.replace("AITA", 'Am I the BLEEP')
    text = text.replace("AITA-", 'Am I the BLEEP')
    text = text.replace("asshole", 'BLEEP')
    text = text.replace("assholes", 'BLEEP')
    text = text.replace("fuck", 'BLEEP')
    text = text.replace("bitch", 'BLEEP')
    text = text.replace("shit", 'BLEEP')

    #Community Guidelines check
    if("kill" in text or "murder" in text or "rape" in text or "rapist" in text or "murdered" in text or "gun" in text):
        print("Text Violation detected. Skipping...")
        continue

    #Determine size of text and whether to split it into multiple chunks of audio
    if(utf8len(text) >= 5000):
        print("Text too large. Skipping...")
        continue

    #Update byte usage
    with open('byteUsage.txt', 'r') as file:
        # read the contents of the file
        contents = file.read()

    # convert the contents to a float (assuming the value is a number)
    old_value = float(contents.strip())

    # add the new value to the old value
    new_value = utf8len(text)
    updated_value = old_value + new_value

    # open the file in write mode and write the updated value
    with open('file.txt', 'w') as file:
        file.write(str(updated_value))

    try:
        print("Converting Text to Speech...")
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request, select the language code ("en-US") and the ssml
        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US", name="en-US-Neural2-J"
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        print("Done Converting Text to Speech!")
        print("Writing Audio to File...")

        # The response's audio_content is binary.
        with open("output_" + str(count) + ".mp3", "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file ' + "output_" + str(count) + ".mp3")

        videoclip = VideoFileClip(BACKGROUND)
        audioclip = AudioFileClip("output_" + str(count) + ".mp3")
        new_audioclip = CompositeAudioClip([audioclip])
        
        videoOffset = random.randint(30, 3600)
        videoclip = videoclip.subclip(videoOffset, new_audioclip.duration + videoOffset)
        videoclip.audio = new_audioclip
        videoclip = videoclip.speedx(1.1)
        videoclip.write_videofile("outputID_" + id + ".mp4", fps=60, threads=12, audio_codec="aac")

        # If modifying these scopes, delete the file token.json.
        SCOPES = ['https://www.googleapis.com/auth/drive.file']

        # If modifying these scopes, delete the file token.json.
        """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('drive', 'v3', credentials=creds)

            file_metadata = {'name': "outputID_" + id + ".mp4",
                            'parents' : [SubredditsAndFolders[SUBREDDIT]]}
            media = MediaFileUpload("outputID_" + id + ".mp4",
                                    mimetype='video/mp4', resumable=True, chunksize=524288*4)

            # Call the Drive v3 API
                    # Call the Drive v3 API
            print("Uploading to Google Drive...")
            request = service.files().create(body=file_metadata, media_body=media, fields='id')
            total_size = int(request.resumable.size())
            pbar = tqdm(total=total_size, unit='B', unit_scale=True)
            media.stream() ### this line doesn't exist in the guide... ###
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    pbar.update(524288*4)

            pbar.close()
            print("Uploaded to Google Drive.")
            
        except HttpError as error:
            # TODO(developer) - Handle errors from drive API.
            print('\a')
            print(f'An error occurred: {error}')

        count+=1
        
    except Exception as e:
        print('\a')
        print(e)
        count+=1