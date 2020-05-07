from collections import deque
from functools import reduce
import os
from os import path

from gtts import gTTS
from dotenv import load_dotenv
import moviepy.editor as mpy
from PIL import Image, ImageDraw, ImageFont
import praw


def text_wrap(text, font, max_width):
    lines = []

    # If the text width is smaller than the image width, then no need to split
    # just add it to the line list and return
    if font.getsize(text)[0] <= max_width:
        lines.append(text)
    else:
        # split the line by spaces to get words
        words = text.split(' ')
        i = 0
        # append every word to a line while its width is shorter than the image width
        while i < len(words):
            line = ''
            while i < len(words) and font.getsize(line + words[i])[0] <= max_width:
                line += words[i] + " "
                i += 1
            if not line:
                line = words[i]
                i += 1
            lines.append(line.strip())
    return lines


# Load environment variables from .env
dotenv_path = path.join(path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# # Get environment variables
# client_id = os.environ['REDDIT_CLIENT_ID']
# client_secret = os.environ['REDDIT_CLIENT_SECRET']

# # Create reddit client
# client_options = {
#     'client_id': client_id,
#     'client_secret': client_secret,
#     'user_agent': 'Reddit Video Generator 0.1 by /u/soorriously'
# }
# client = praw.Reddit(**client_options)

# askreddit = client.subreddit('askreddit')
# for question in askreddit.hot(limit=10):
#     if not question.stickied:
#         selected = question
#         break

# comments = []
# for c in list(selected.comments):

#     if (type(c) is praw.models.MoreComments
#         or c.body == '[deleted]'
#         or c.author == None
#         ):
#         continue
#     comments.append((c.author.name, c.body)

# test data
comments = [
    # ('solemove', 'Great great grandpa is John Nordstrom. He ran a department store in Seattle'),
    # ('PM_ME_AMAZONGIFTCODE', 'I would be surprised if I am not related to Genghis Khan since he supposedly had hundreds of children.'),
    ('GrumpyCTurtle', 'While the specific name has been lost to history, had a great grandmother trace the family history and Sigil/Crest all the way back to a small town in what is now England where the noble sport of Falconry was born.\n\nGrew up with a kid whose great aunt was Eva Braun, the infamous trist to Adolf Hitler.' * 5),
    # ('AtelierAndyscout', 'John Sutter. Discovered gold in California (well, his employee did). \n\nSupposedly he was my great, great, great (x?) uncle.'),
]

font_size = 20
font = ImageFont.truetype('fonts/IBMPlexSans-Regular.ttf', font_size)

# Generate audio & pictures
extra_imgs = 0
for i, (author, body) in enumerate(comments):
    paragraphs = [p for p in body.split('\n') if p != '']
    lines = []
    for p in paragraphs:
        if lines:
            lines.append(' ')  # Gap between paragraphs
        lines.extend(text_wrap(p, font, 480))

    img = Image.new('RGB', (500, 500), color='#181B28')
    draw = ImageDraw.Draw(img)

    y_offset = 10
    line_height = font_size * 1.1
    num_lines = len(lines)
    tts_start, tts_end = 0, 0
    for j, l in enumerate(lines):
        draw.text((10, y_offset), l, fill='#eeeeee', font=font)

        if l == ' ':
            y_offset += line_height / 2
        else:
            y_offset += line_height

        if y_offset + line_height + 10 >= 500:
            img.save(f'assets/img{i + extra_imgs}.jpg')
            y_offset = 10
            img = Image.new('RGB', (500, 500), color='#181B28')
            draw = ImageDraw.Draw(img)
            tts_start, tts_end = tts_end, j + 1
            tts = gTTS(' '.join(lines[tts_start:tts_end]))
            tts.save(f'assets/vo{i + extra_imgs}.mp3')
            extra_imgs += 1

    img.save(f'assets/img{i + extra_imgs}.jpg')
    tts = gTTS(' '.join(lines[tts_end:]))
    tts.save(f'assets/vo{i + extra_imgs}.mp3')

clips = []
for i in range(len(comments) + extra_imgs):
    # Do the video
    a_clip = mpy.AudioFileClip(f'assets/vo{i}.mp3')
    i_clip = mpy.ImageClip(
        f'assets/img{i}.jpg',
        duration=a_clip.duration
    ).set_audio(a_clip)
    clips.append(i_clip)

final_video = mpy.concatenate_videoclips(clips)

if not path.exists('dist'):
    os.mkdir('dist')

final_video.write_videofile('dist/output.mp4', fps=30)
