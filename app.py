from flask import Flask
from flask import make_response

app = Flask(__name__)

##############################
# IMPORT OTHER PY DEPENDENCIES
##############################

import json
import requests
import feedparser

from bs4 import BeautifulSoup
from collections import defaultdict

##############################
# 1 / FROM RSS: GET TODAY'S URL
##############################

url = 'https://www.theguardian.com/media/news-photography/rss'
feed = feedparser.parse(url)

lastest_url = feed.entries[0]['link']
# lastest_date = feed.entries[0]['date'] # add conversion for later usage

response = requests.get(lastest_url).text
# double failsafe for entries that are no galleries
if 'is-immersive' not in response:
	lastest_url = feed.entries[1]['link']
	response = requests.get(lastest_url).text

	if 'is-immersive' not in response:
		lastest_url = feed.entries[2]['link']
		response = requests.get(lastest_url).text

##############################
# 2 / FROM HTML: GET DATA
##############################
soup = BeautifulSoup(response, 'html.parser')

# DEFINE LISTS
photo_urls = []
photo_titles = []
photo_captions = []
photo_credits = []

photos = defaultdict(dict)
# photos['test'] = 'some text'
photos['items'] = {}

# GET THE photo_urls OUT OF THE SOUP
for photoset in soup.find_all('source', media='(min-width: 1300px) and (-webkit-min-device-pixel-ratio: 1.25), (min-width: 1300px) and (min-resolution: 120dpi)'):
	photo_url = str(photoset.attrs['srcset']).replace(' 2020w','')
	photo_url = photo_url.replace(' 3800w','')
	photo_urls.append(photo_url)

# GET THE photo_captions OUT OF THE SOUP
for photo_caption in soup.find_all('div', class_='gallery__caption'):
	photo_caption = photo_caption.text
	# photo_caption = photo_caption.split('\n',2)[2]
	photo_caption = photo_caption.replace('\r',' ').replace('\n',' ').replace(' ',' ').replace('   ','').replace('  ','')
	photo_captions.append(photo_caption)

# GET THE photo_titles OUT OF THE SOUP
for photo_title in soup.find_all('h2', class_='gallery__caption__title'):
	photo_titles.append(str(photo_title.text))

# GET THE photo_credits OUT OF THE SOUP
for photo_credit in soup.find_all('p', class_='gallery__credit'):
	photo_credit = photo_credit.text.replace('Photograph: ','')
	photo_credits.append(photo_credit)

##############################
# 3 / PREPARE FISH 4 SELLING
##############################
for index,photo_url in enumerate(photo_urls):
	
	i = index - 1

	item = {
		'url': photo_url,
		'title': photo_titles[i],
		'caption': photo_captions[i],
		'copyright': photo_credits[i]
		}

	photos['items'].update(
			{
				index : item
			}
		)

##############################
# 4 / CONVERT TO JSON
##############################
json_feed = json.dumps(photos)

##############################
# 5 / OUTPUT JSON
##############################
@app.route('/')
def the_output(json_feed=json_feed, headers=None):
    resp = make_response(json_feed)
    resp.mimetype = 'application/json'
    return resp

if __name__ == '__main__':
	app.run(debug=True, use_reloader=True)