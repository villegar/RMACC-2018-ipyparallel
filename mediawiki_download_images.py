# functions to download images from mediwiki using the api
#
# adapted from from
# http://nbviewer.jupyter.org/github/minrk/IPython-parallel-tutorial/blob/master/images.ipynb. (updated to python3)

import sys, os

import requests

api_url = "https://commons.wikimedia.org/w/api.php"

def wikimedia_api_request(**kwargs):
    """ Make a request of the Wikimedia Commons API
        Returns data after parsing JSON
    """
    sys.stdout.write('.')
    sys.stdout.flush()
    
    params = dict(action='query', format='json', )
    params.update(kwargs)
    r = requests.get(api_url, params=params)
    r.raise_for_status()
    return r.json()

import json

def search_images(search, limit=100, size_limit=80000000):
    """search wikimedia commons for a given term
    
    returns a list of `limit` URLs for images
    """
    urls = []
    continue_params = {}
    while limit > 0:
        data = wikimedia_api_request(
                srnamespace=6,
                prop='imageinfo',
                list='search',
                srsearch=search,
                srlimit=min(limit, 50),
                **continue_params
        )
#        continue_params = data['query-continue']['search']
        total = data['query']['searchinfo']['totalhits']
        results = data['query']['search']
        for r in results:
            title = r['title']
            data = wikimedia_api_request(
                            prop='imageinfo',
                            titles=title,
                            iiprop='url|size|mime')
            imageinfo = list(data['query']['pages'].values())[0]['imageinfo'][0]
            if imageinfo['mime'] in ('image/png', 'image/jpeg') and imageinfo['size'] <= size_limit:
                urls.append(imageinfo['url'])
                limit -= 1
 
    return urls

def download_images(search, n):
    """download images from mediawiki commons to folders based on the search term"""
    if not os.path.exists('images'):
        os.mkdir('images')
    tagdir = os.path.join('images', search)
    if not os.path.exists(tagdir):
        os.mkdir(tagdir)
    for url in search_images(search, n):
        r = requests.get(url)
        fname = url.rsplit('/')[-1]
        dest = os.path.join(tagdir, fname)
        # print("downloading %s => %s" % (url, dest))
        sys.stdout.write('+')
        sys.stdout.flush()
        with open(dest, 'wb') as f:
            f.write(r.content)
