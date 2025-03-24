import requests
import base64
import random
from flask import render_template


class Spotify_API:
    CLIENT_ID = 'Client_Id'
    CLIENT_SECRET = 'Client_Secret'
    ACCESS_TOKEN: str
    id_secret_base64: str
    client_credentials_url = 'https://accounts.spotify.com/api/token'
    new_releases_url = 'https://api.spotify.com/v1/browse/new-releases'
    album_url = 'https://api.spotify.com/v1/albums/'  # + id
    tracks_url = 'https://api.spotify.com/v1/tracks/'  # + id
    audio_features_url = 'https://api.spotify.com/v1/audio-features/'  # + id
    body_params: dict
    header_params: dict
    album_info: dict
    track_info: dict
    track_features: dict
    error = False

    def __init__(self):
        # Create a base64 encoded string, required for getting an access token
        id_secret_text = '{client_id}:{client_secret}'.format(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET)
        self.id_secret_base64 = base64.b64encode(
            id_secret_text.encode("ascii")).decode("ascii")
        self._get_access_token()

# ----- Get an access token
    def _get_access_token(self):
        # Body and header parameters, required for POST request
        self.body_params = {'grant_type': 'client_credentials'}
        self.header_params = {
            'Authorization': 'Basic {id_secret_base64}'.format(
                id_secret_base64=self.id_secret_base64)}

        # POST request
        response = requests.post(
            self.client_credentials_url,
            headers=self.header_params,
            data=self.body_params)

        # Check if request was successful
        if response:
            self.ACCESS_TOKEN = response.json()['access_token']
            self._get_new_releases()
        else:
            self.error = True
            return render_template(
                "process.html", text='An error has occurred.')

# ----- Get data about new releases
    def _get_new_releases(self):
        # Header parameters for GET request
        self.header_params = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer {access_token}'.format(
                access_token=self.ACCESS_TOKEN)}
        response = requests.get(
            self.new_releases_url,
            headers=self.header_params)

        # Check if request was successful
        if response:
            self._parse_release(response)
        else:
            self.error = True
            return render_template(
                "process.html", text='An error has occurred.')

# ----- Divide new releases into albums and singles
    def _parse_release(self, response):
        albums = []
        singles = []
        for item in response.json()['albums']['items']:
            if item['album_type'] == 'single':
                singles.append(item['id'])
            else:
                albums.append(item['id'])
        self.error, info = self._get_random_album(albums)
        if not self.error:
            self.album_info = info
            self._get_random_track(singles)

# ----- Get data about an album
    def _get_random_album(self, albums: list):
        album_id = random.choice(albums)
        album_url = self.album_url + album_id
        # same header params as in "New Realeses"
        response = requests.get(album_url, headers=self.header_params)
        if response:
            return False, response.json()
        else:
            return True, render_template(
                "process.html", text='An error has occurred.')

# ----- Get data about a track + get audio features for a track
    def _get_random_track(self, singles):
        # First, parse single as an ordinary album
        self.error, single = self._get_random_album(singles)

        if not self.error:
            # Extracting information about one and only track in a single album
            single_id = single['tracks']['items'][0]['id']
            single_url = self.tracks_url + single_id
            # same headers
            response = requests.get(single_url, headers=self.header_params)

            # Check response
            if response:
                self.track_info = response.json()

                # Extract audio features
                audio_features_url = self.audio_features_url + single_id
                # same headers
                response = requests.get(
                    audio_features_url, headers=self.header_params)
                if response:
                    self.track_features = response.json()
                else:
                    self.error = True
                    return render_template(
                        "process.html", text='An error has occurred.')
            else:
                self.error = True
                return render_template(
                    "process.html", text='An error has occurred.')
