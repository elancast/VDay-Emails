import os, sys
import urllib
import json
import time

TEMPLATE = 'template.html'
TEMPLATE_ITEM = 'template-item.html'
TEMPLATE_REDDIT = 'template-reddit.html'

ASTRO_URL = 'http://apod.nasa.gov/apod/'
BING_URL = 'http://feeds.feedburner.com/bingimages'
NAT_GEO_URL = 'http://photography.nationalgeographic.com/photography/photo-of-the-day/'
PUN_URL = 'http://feeds.feedburner.com/PunOfTheDay'
WEATHER_URL = 'http://www.weather.com/weather/tomorrow/San+Francisco+CA+94115:4:US'
XKCD_URL = 'http://xkcd.com/'

IMAGES_FROM_REDDIT = 3
SLEEP_TIME_BETWEEN = 1
SLEEP_TIME_ERROR = 10

class HtmlFormerV2:
  def __init__(self):
    html = self.initTemplates()
    (self.template, self.template_item, self.template_reddit) = html

  ##############################################################################
  # Templates code
  ##############################################################################

  def initTemplates(self):
    f = open(TEMPLATE, 'r')
    template = f.read()
    f.close()
    f = open(TEMPLATE_ITEM, 'r')
    template_item = f.read()
    f.close()
    f = open(TEMPLATE_REDDIT, 'r')
    template_reddit = f.read()
    f.close()
    return (template, template_item, template_reddit)

  def formReddit(self, subreddit, user, image, text, perma, imagelink = None):
    if imagelink == None: imagelink = image
    s = self.template_reddit.replace('\\\\\\imagelink', imagelink)
    s = s.replace('\\\\\\image', image)
    s = s.replace('\\\\\\postlink', perma)
    s = s.replace('\\\\\\subreddit', subreddit)
    s = s.replace('\\\\\\user', user)
    return s.replace('\\\\\\text', text)

  def formItem(self, image, title, text, imagelink = None):
    if imagelink == None: imagelink = image
    s = self.template_item.replace('\\\\\\imagelink', imagelink)
    s = s.replace('\\\\\\image', image)
    s = s.replace('\\\\\\title', perma)
    return s.replace('\\\\\\text', subreddit)

  def formEmail(self, bing, xkcd, weather, pun, content):
    s = self.template.replace('\\\\\\bing-link', bing['link'])
    s = s.replace('\\\\\\bing-image', bing['img'])
    s = s.replace('\\\\\\bing-text', bing['text'])
    s = s.replace('\\\\\\xkcd-link', xkcd['link'])
    s = s.replace('\\\\\\xkcd-image', xkcd['img'])
    s = s.replace('\\\\\\weather-descr', weather['descr'])
    s = s.replace('\\\\\\weather-temp', weather['temp'])
    s = s.replace('\\\\\\weather-image', weather['img'])
    s = s.replace('\\\\\\pun-text', pun)
    return s.replace('\\\\\\content', content)

  ##############################################################################
  # Parsing non-reddit websites
  ##############################################################################

  def getBing(self):
    content = {}
    s = self.goToTheInternets(BING_URL)
    tag = '![CDATA['

    while tag in s:
      start = s.index(tag) + len(tag)
      end = len(s[start:])
      if tag in s[start:]: end = s.index(tag, start)
      part = s[start : end]
      s = s[end:]
      if not '(Bing United States)' in part: continue

      # Description
      end = part.index(']]')
      desc = part[:end]
      if '(' in desc:
        desc = desc[ : desc.index('(')].strip()
      content['text'] = desc

      # Image link
      tag = 'enclosure url="'
      start = part.index(tag) + len(tag)
      end = part.index('"', start)
      content['img'] = part[start : end]
      content['link'] = 'http://www.bing.com'

      print 'got bing'
      return content

  def getXKCD(self):
    content = {}
    s = self.goToTheInternets(XKCD_URL)

    full = s
    try:
      s = s[s.index('id="comic"'):]
      s = s[s.index('img') - 1:]
      s = s[:s.index('>') + 1]
      s = s[s.index('src="') + 5:]
      content['img'] = s[:s.index('"')]
    except:
      content['link'] = ''
      content['img'] = ''
      return content

    # Find perma link
    tag = 'Permanent link to this comic:'
    start = full.find(tag)
    if start >= 0:
      start += len(tag)
      end = full.index('<', start)
      content['link'] = full[start : end].strip()
    else:
      content['link'] = XKCD_URL

    print 'got xkcd'
    return content

  def getWeather(self):
    content = {}
    s = self.goToTheInternets(WEATHER_URL)
    s = s[s.index('"wx-forecast-container"'):]
    s = s[s.index('<img'):]
    img = s[s.index('rc="') + 4:]
    content['img'] = img[:img.index('"')]

    key = 'wx-temp'
    temp = s[s.index(key) + len(key):]
    temp = temp[temp.index('>') + 1:]
    temp = temp[:temp.index('<')].strip()
    content['temp'] = temp

    phrase = s[s.index('wx-phrase'):]
    content['descr'] = phrase[phrase.index('>') + 1 : phrase.index('<')]
    print 'got weather'
    return content

  def getPun(self):
    s = self.goToTheInternets(PUN_URL)
    s = s[s.index('<item>'):]
    tag = '<description>'
    start = s.index(tag) + len(tag)
    end = s.index('&lt;', start)
    print "got pun"
    return s[start : end]

  ##############################################################################
  # Reddit
  ##############################################################################

  def getRedditApiUrl(self, subreddit):
    return 'http://www.reddit.com/r/%s.json' % subreddit

  def getSubreddit(self, subreddit):
    for i in range(4):
      try:
        s = self.goToTheInternets(self.getRedditApiUrl(subreddit))
        parsed = json.loads(s)
        posts = parsed['data']['children']
        break
      except:
        print 'ERROR for subreddit %s: %s' % (subreddit, s[:25])
        time.sleep(SLEEP_TIME_ERROR)

    poss = []
    for post in posts:
      data = post['data']
      if not 'url' in data: continue
      (url, title, domain, perma, user) = \
          (data['url'], data['title'], data['domain'], data['permalink'],
           data['author'])
      if 'self.' in domain: continue
      if 'imgur' in domain and not '.' in url[len(url) - 4:]: url += '.jpg'
      if not '.' in url[len(url) - 4:]: continue
      perma = 'http://www.reddit.com%s' % perma
      isAlbum = '/a/' in url or '/gallery/' in url
      position = len(poss) + (100 if isAlbum else 0)
      poss.append((user, url, title, perma, isAlbum, position))

    poss.sort(key=lambda i: i[4])
    print 'got %s: %d stories' % (subreddit, len(poss))
    poss = poss[:IMAGES_FROM_REDDIT]
    htmls = map(
      lambda i: self.formReddit(subreddit, i[0], i[1], i[2], i[3], i[1]), poss)
    return ''.join(htmls)

  ##############################################################################
  # Main
  ##############################################################################

  def goToTheInternets(self, url, count = 1):
    time.sleep(SLEEP_TIME_BETWEEN)
    try:
      return urllib.urlopen(url).read()
    except:
      print 'CALL FAILED. RETRYING'
      if count > 4: return ''
      time.sleep(SLEEP_TIME_ERROR)
      return self.goToTheInternets(url, count + 1)

  def getHTML(self):
    # Non-reddit content
    # TODO

    # Reddit
    subreddits = [ 'aww', 'skyrim', 'earthporn' ]
    subreddits = [ 'aww' ]
    content = ''.join(map(lambda i: self.getSubreddit(i), subreddits))

    # Non-reddit special content
    bing = self.getBing()
    xkcd = self.getXKCD()
    weather = self.getWeather()
    pun = self.getPun()

    return self.formEmail(bing, xkcd, weather, pun, content)

if __name__ == "__main__":
  import sys
  f = open(sys.argv[1], 'w')
  html = HtmlFormerV2().getHTML()
  f.write(html)
  f.close()
