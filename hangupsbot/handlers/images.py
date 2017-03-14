import re
import urllib.request
import hangups
import random
import os

from hangupsbot.utils import word_in_text, text_to_segments
from hangupsbot.handlers import handler


def download(url, name):
    with urllib.request.urlopen(url) as response, open(name, 'wb') as out_file:
        data = response.read() # a `bytes` object
        out_file.write(data)

@handler.register(priority=7, event=hangups.ChatMessageEvent)
def handle_image(bot, event):
    """Handle autoreplies to keywords in messages"""
    # Test if message is not empty
    if not event.text:
        return

    # Test if autoreplies are enabled
    #if not bot.get_config_suboption(event.conv_id, 'autoreplies_enabled'):
    #    return

    # Test if there are actually any autoreplies
    #autoreplies_list = bot.get_config_suboption(event.conv_id, 'autoreplies')
    #if not autoreplies_list:
    #    return
    links = re.findall('(https?://\S+(?:jpg|gif|png))', event.text)
    if len(links) == 0: 
        return
    for link in links:
        file_end = re.search('(...)$', link)
        file_path = '/tmp/hg-image-' + str(random.randint(0,100))+'.'+file_end.groups()[0]
        download(link, file_path)
        file = open(file_path, 'rb')
        yield from event.conv.send_message(text_to_segments(''), file)
        file.close()
        os.remove(file_path)
   
