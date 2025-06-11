# app.py
from flask import Flask, render_template, request
import re
import os
import base64
from datetime import datetime

app = Flask(__name__)
app.config['M3U8_FILE'] = 'playlist.m3u8'

def parse_m3u8(file_path):
    """Parse M3U8 file with extended metadata"""
    channels = []
    categories = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return {}

    i = 0
    channel_id = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF'):
            # Extract metadata
            channel = {'id': channel_id}
            channel_id += 1

            # Extract channel name
            name_match = re.search(r',(.*)$', line)
            if name_match:
                channel['name'] = name_match.group(1).strip()

            # Extract attributes
            attr_matches = re.findall(r'(\w+-\w+)="([^"]+)"', line)
            for key, value in attr_matches:
                channel[key] = value

            # Get stream URL
            if i + 1 < len(lines):
                channel['url'] = lines[i+1].strip()
                i += 1

            # Add to category
            category = channel.get('group-title', 'Uncategorized')
            if category not in categories:
                categories[category] = []
            categories[category].append(channel)
        i += 1

    return categories

@app.route('/')
def index():
    categories = parse_m3u8(app.config['M3U8_FILE'])
    # Grab selected_category from the URL (?selected_category=News), default to first
    selected_category = request.args.get('selected_category')
    if not selected_category and categories:
        selected_category = next(iter(categories.keys()))

    return render_template('index.html',
                           categories=categories,
                           selected_category=selected_category,
                           current_time=datetime.now().strftime("%Y-%m-%d %H:%M"),
                           current_year=datetime.now().year)

@app.route('/channel/<int:channel_id>')
def play_channel(channel_id):
    categories = parse_m3u8(app.config['M3U8_FILE'])

    # Find the channel by ID
    channel = None
    for cat in categories.values():
        for ch in cat:
            if ch['id'] == channel_id:
                channel = ch
                break
        if channel:
            break

    if not channel:
        return "Channel not found", 404

    return render_template('player.html',
                           channel=channel,
                           categories=categories,
                           current_time=datetime.now().strftime("%Y-%m-%d %H:%M"))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
