from flask import Flask, render_template
from process import Spotify_API

app = Flask(__name__)


# Starting page
@app.route('/')
def start():
    return render_template('start.html')


# Stuff, considering data extracting and saving + further display
@app.route('/process')
def process():
    sa = Spotify_API()
    if not sa.error:
        return render_template(
            'result.html', album=sa.album_info, track=sa.track_info, album_artists=artists(
                sa.album_info['artists']), track_artists=artists(
                sa.track_info['artists']), track_features=audio_features(
                sa.track_features))


# Help function - extracts information about artists into a pretty string
def artists(artists_: list):
    ans = ''
    for i in range(len(artists_)):
        if i != 0:
            ans += ', '
        ans += artists_[i]['name']
    return ans


# Help function - extracts only necessary information from audio features
def audio_features(features: dict):
    ans = ''
    ans += 'Duration: ' + str(int(features['duration_ms'] / 1000 / 60)) + ':' + '{:02d}'.format(
        int(features['duration_ms'] / 1000) - int(features['duration_ms'] / 1000 / 60) * 60) + '\n'
    ans += 'Danceability: ' + str(features['danceability']) + '\n'
    ans += 'Energy: ' + str(features['energy'])
    return ans


if __name__ == '__main__':
    # Launch the Flask dev server
    app.run(host="localhost", port=5000, debug=True)
