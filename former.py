import os, sys
import urllib
import json
import time

ASTRO_URL = 'http://apod.nasa.gov/apod/'
BING_URL = 'http://feeds.feedburner.com/bingimages'
NAT_GEO_URL = 'http://photography.nationalgeographic.com/photography/photo-of-the-day/'
PUN_URL = 'http://feeds.feedburner.com/PunOfTheDay'
XKCD_URL = "http://xkcd.com/"

HTML_TEMPLATE_FILE = 'email.html'
SLEEP_TIME_BETWEEN = 3
SLEEP_TIME_ERROR = 10

class HtmlFormer:
  def __init__(self):
    self.html = ''
    self._formEmail()

  def getHtml(self):
    return self.html

  def goToTheInternets(self, url, sleep=True, count=1):
    if sleep: time.sleep(SLEEP_TIME_BETWEEN)
    try:
      return urllib.urlopen(url).read()
    except:
      print "CALL FAILED. RETRYING"
      if count > 3: return ''
      time.sleep(SLEEP_TIME_ERROR)
      return self.goToTheInternets(url, sleep, count + 1)

  def getFormattedTitle(self, text):
    st = 'color:#483D8B;'
    return '<h4 style="%s">%s</h4>' % (st, text)

  """ Returns XKCD html """
  def getXkcdHtml(self):
    s = self.goToTheInternets(XKCD_URL)
    full = s
    try:
      s = s[s.index('id="comic"'):]
      s = s[s.index('img') - 1:]
      s = s[:s.index('>') + 1]
    except:
      return ''

    # Find perma link
    tag = 'Permanent link to this comic:'
    start = full.find(tag)
    if start >= 0:
      start += len(tag)
      end = full.index('<', start)
      url = full[start : end].strip()
    else:
      url = XKCD_URL

    place = s.index(' ')
    insert = 'width=300'
    img = s[:place + 1] + insert + s[place:]
    title = self.getFormattedTitle('The latest XKCD is...')
    print 'got xkcd'
    return '%s<a href="%s">%s</a>' % (title, url, img)

  """ Takes the data from poss which is r/awww to convert to html """
  def convertRedditImgsToHtml(self, poss):
    maxPics = 3; i = 0
    htmls = []
    for x in poss:
      if i == maxPics: return htmls
      i += 1
      (url, reddit, title) = x[:3]
      img = '<a href="%s"><img src="%s" title="%s" width=300 /></a>'\
          % (url, url, title)
      if len(x) > 3 and x[3]:
        img = img.replace('img src', 'a href')
        img = img.replace('/>', '>Check out the imgur album!</a>')
      descr = 'Read Reddit\'s take on this image <a href="%s">here</a>.%s'\
          % (reddit, '<br><br>')
      if len(x) > 4 and x[4] != None:
        add = 'You can also view its Flickr page <a href="%s">here</a>.' % x[4]
        descr = descr.replace('.<br', '. %s<br' % add)
      html = [ self.getFormattedTitle(title), descr, img ]
      htmls.append(''.join(html))
    return htmls

  """ Returns some html from aww reddit """
  def getAww(self):
    return self.getSubreddit('aww')

  """ Returns the bing picture """
  def getBing(self):
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

      # Image link
      tag = 'enclosure url="'
      start = part.index(tag) + len(tag)
      end = part.index('"', start)
      url = part[start : end]

      # HTML!
      title = self.getFormattedTitle('Today\'s Bing picture is...')
      print 'got bing'
      return '%s%s<br><br><a href=%s><img src="%s" width=300 title="%s" /></a>'\
          % (title, desc, url, url, desc)
    return ''

  def getAstronomyVideoThoseFuckers(self, s):
    tag = '<iframe '
    if not tag in s: return None
    start = s.index(tag)
    start = s.index('http', start)
    end = s.index('"', start)
    return (s[start:end], end)

  def getAstronomy(self):
    tag = 'IMG SRC="'
    s = self.goToTheInternets(ASTRO_URL)

    # Videos goddammit...
    vid = False
    if not tag in s:
      ret = self.getAstronomyVideoThoseFuckers(s)
      if ret == None: return ''
      (url, end) = ret
      vid = True

    else:
      # Get the image
      start = s.index(tag) + len(tag)
      end = s.index('"', start)
      url = s[start : end]
      if not 'http://' in url: url = ASTRO_URL + url

      # Get the description
      tag = '<b>'
      start = s.index(tag, end) + len(tag)
      end = s.index('<', start)
      descr = s[start : end].strip()

      # Get the date
      start = s.index('?date=') + len('?date=')
      end = s.index('"', start)
      date = s[start : end]
      perma = '%sap%s.html' % (ASTRO_URL, date)

    # Also get some text about the image
    desc = ''
    marker = '<b> Explanation: </b>'
    if marker in s:
      start = s.index(marker) + len(marker)
      end = s.index('Tomorrow\'s picture:', start)
      desc = self.stripTags(s[start : end])
      if '.' in desc:
        desc = desc[:desc.index('.') + 1]
      desc = '%s<br><br>' % desc

    # Do it!
    title = self.getFormattedTitle(
      'Today\'s Astronomy Picture of the Day is...')
    if not vid:
      img = '<a href="%s"><img src="%s" title="%s" width=300 /></a>' % \
          (perma, url, descr)
    else:
      img = '<a href="%s">%s</a>' % (url, descr)
    print 'got astronomy'
    return title + desc + img

  def stripTags(self, s):
    ret = []; i = 0
    while i < len(s):
      if s[i] == '<':
        while i < len(s) and s[i] != '>': i += 1
      else:
        ret.append(s[i])
      i += 1
    return ''.join(ret).strip()

  """ Returns a pun from a daily pun site """
  def getPun(self):
    s = self.goToTheInternets(PUN_URL)
    s = s[s.index('<item>'):]
    tag = '<description>'
    start = s.index(tag) + len(tag)
    end = s.index('&lt;', start)
    pun = s[start : end]
    msg = 'Puns stolen from <a href="http://www.punoftheday.com/">%s</a>.'\
        % 'Pun of the Day'
    title = self.getFormattedTitle('Today\'s daily pun is...')
    print "got pun"
    return '%s%s<br><br>%s<br>' % (title, pun, msg)

  def getEarthPorn(self):
    return self.getSubreddit('EarthPorn')

  def getCityPorn(self):
    return self.getSubreddit('CityPorn')

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
      (url, title, domain, perma) = \
          (data['url'], data['title'], data['domain'], data['permalink'])
      if 'self.' in domain: continue
      if 'imgur' in domain and not '.' in url[len(url) - 4:]: url += '.jpg'
      if not '.' in url[len(url) - 4:]: continue
      perma = 'http://www.reddit.com%s' % perma
      isAlbum = '/a/' in url or '/gallery/' in url
      position = len(poss) + (100 if isAlbum else 0)
      poss.append((url, perma, title, isAlbum, position))
    poss.sort(key=lambda i: i[3])
    poss = map(lambda i: i[:3], poss)
    print 'got %s: %d stories' % (subreddit, len(poss))
    return self.convertRedditImgsToHtml(poss)

  def getZelda(self):
    return self.getSubreddit('zelda')

  def getPoke(self):
    return self.getSubreddit('pokemon')

  def getNatGeo(self):
    s = self.goToTheInternets(NAT_GEO_URL)
    s = s[s.index('primary_photo'):]

    # The image
    before = '<img src="'
    start = s.index(before) + len(before)
    after = s.index('"', start)
    img = s[start:after]

    # The caption
    before = 'alt="'
    start = s.index(before) + len(before)
    end = s.index('"', start)
    caption = s[start:end]

    # Form stuff and return
    title = self.getFormattedTitle('Today\'s National Geographic picture is...')
    it = '<a href="%s"><img src="%s" title="%s" width=300 /></a>'\
        % (img, img, caption)
    print 'got natgeo'
    return '%s%s<br><br>%s' % (title, caption, it)

  def getTemplate(self):
    filename = os.path.join(os.path.dirname(sys.argv[0]), HTML_TEMPLATE_FILE)
    f = open(filename, 'r')
    s = f.read()
    f.close()
    return s

  """ Calls the different functions necessary to generate all of the
  HTML and then forms the HTML document """
  def _formEmail(self):
    fns = [
      self.getXkcdHtml, self.getBing,
      self.getAstronomy, self.getPun,
      self.getNatGeo, self.getAww,
      self.getZelda, self.getCityPorn,
      self.getPoke, self.getEarthPorn
    ]

    htmls = []
    for fn in fns:
      try:
        ret = fn()
        if type(ret) == type(''): htmls.append(ret)
        else: htmls += ret
      except:
        pass

    # Starter html for top of page
    html = self.getTemplate()

    # Fill in the table
    i = 0
    while i < len(htmls):
      html += '\n\n<tr style="vertical-align: top;">'
      for j in range(2):
        if i >= len(htmls): break
        html += '\n<td style="width:300px;">%s</td>' % htmls[i]
        i += 1
      html += '\n</tr>'
      self.html = html + '</table></tr></td></table>'

# TESTING CODE
if __name__ == "__main__":
  import sys
  f = open(sys.argv[1], 'w')
  html = HtmlFormer().getHtml()
  f.write(html)
  f.close()
