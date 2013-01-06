import os, sys
import urllib
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

  def getFlickrImageLink(self, part):
    # Get the URL to go to... (blegh)
    url = 'www.flickr.com'
    if not url in part: return None
    start = part.index(url)
    if '&#34;' in part[start:]: end = part.index('&#34;', start)
    elif '"' in part[start:]: end = part.index('"', start)
    else: return None
    url = 'http://' + part[start : end]

    # Open it...
    s = self.goToTheInternets(url, sleep=False)

    # Nice tag. So nice. It's a big, downloadable image. Yay!
    tag = '<div id="allsizes-photo">'
    if tag in s:
      start = s.index(tag)
      tag = 'src="'
      start = s.index(tag, start) + len(tag)
      end = s.index('"', start)
      return (url, s[start : end])

    # Look for tag
    tag = 'rel="image_src"'
    if not tag in s: return None
    start = s.index(tag)
    tag = 'href="'
    start = s.index(tag, start) + len(tag)
    end = s.index('"', start)
    happy = s[start : end]

    # Find the larger image link
    options = [ '_b.jpg', '_o.jpg', '_c.jpg', '_z.jpg', '_m.jpg' ]
    if options[-1] in happy:
      ind = 0
      for ind in range(len(options)):
        happy = happy.replace(options[ind - 1], options[ind])
        if happy in s: break
        print 'tried ' + options[ind] + ' and no go :('
      return (url, happy)

  """ Returns the title of the reddit link """
  def getRedditPartTitle(self, part, link):
    tag = 'title=&#34;'
    if not tag in part: return None
    start = part.index(tag) + len(tag)
    if '&#34;' in part[start:]: end = part.index('&#34;', start)
    elif '"' in part[start:]: end = part.index('"', start)
    else: return None
    title = part[start : end]
    if "Porn" in link and '[' in title:
      title = title[:title.index('[')].strip()
    return title

  """ Returns the imgur link from the reddit part """
  def getImgurImageLink(self, part):
    if not 'imgur.com/' in part: return None
    if 'imgur.com/a/' in part: return None
    cut = part.index('imgur.com/')
    start = part.index('/', cut) + 1
    end = start
    while part[end] != '.' and part[end] != '&': end += 1
    url = 'http://imgur.com/%s.jpg' % part[start : end]
    return url

  """ Parses out all of the images from the string provided """
  def getRedditImages(self, s, link):
    (st, en) = ('<description>', '</description>')
    poss = []
    while st in s:
      if len(poss) >= 4: break
      start = s.index(st) + len(st)
      end = s.index(en, start + 1)
      part = s[start : end]
      s = s[end:]

      # Check imgur...
      (flickrPage, img) = (None, None)
      img = self.getImgurImageLink(part)

      # Check flickr...
      flickr = self.getFlickrImageLink(part)
      if flickr != None: (flickrPage, img) = flickr
      if img == None: continue

      # Get reddit link
      start = part.index(link)
      if '&#34;' in part[start:]: end = part.index('&#34;', start)
      elif '"' in part[start:]: end = part.index('"', start)
      else: continue
      reddit = part[start : end]

      # Get the title
      title = self.getRedditPartTitle(part, link)
      if title == None: continue

      # Yayyy
      poss.append( (img, reddit, title, False, flickrPage) )
    return self.convertRedditImgsToHtml(poss)

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

  def getFromReddit(self, url):
    s = self.goToTheInternets(url)
    while "<title>Too Many Requests</title>" in s:
      print "REDDIT WAS A JERKFACE"
      time.sleep(SLEEP_TIME_ERROR)
      s = self.goToTheInternets(url)
    return s

  def getRedditStuff(self, urlstart):
    s = self.getFromReddit(urlstart + ".rss")
    return self.getRedditImages(s, urlstart)

  """ Returns some html from aww reddit """
  def getAww(self):
    urlstart = "http://www.reddit.com/r/aww/"
    a = self.getRedditStuff(urlstart)
    print 'got aww'
    return a

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
      print 'Tagless: %s' % desc
      if '.' in desc:
        desc = desc[:desc.index('.') + 1]
      print 'Final: %s' % desc
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
    urlstart = "http://www.reddit.com/r/EarthPorn/"
    a = self.getRedditStuff(urlstart)
    print "got earth porn"
    return a

  def getCityPorn(self):
    a = self.getRedditStuff("http://www.reddit.com/r/CityPorn/")
    print "got city porn"
    return a

  def getZelda(self):
    url = "http://www.reddit.com/r/zelda/"
    s = self.getFromReddit(url + '.rss')
    poss = []; tab = '<item>'
    while tab in s:
      start = s.index(tab) + len(tab)
      end = s.index('</item>', start)
      part = s[start : end]
      s = s[end:]
      if not 'imgur' in part: continue

      # Find the imgur url
      cut = part.index('imgur')
      start = part.index('/', cut) + 1
      end = start
      while part[end] != '.' and part[end] != '&': end += 1
      url = 'http://imgur.com/%s.jpg' % part[start : end]
      isAlbum = False
      if '/a/' in url:
        url = url[:len(url) - 4]
        isAlbum = True

        # Find the title
        ta = '<title>'
        start = part.index(ta) + len(ta)
        end = part.index('</title', start)
        title = part[start : end].strip()

        # Reddit link
        ta = '<link>'
        start = part.index(ta) + len(ta)
        end = part.index("</", start)
        link = part[start : end].strip()

        # Append! (can call above code yay)
        poss.append( (url, link, title, isAlbum) )
    print 'got zelda %d %d' % (len(poss), len(s))
    return self.convertRedditImgsToHtml(poss)

  def getPoke(self):
    a = self.getRedditStuff("http://www.reddit.com/r/pokemon/")
    print "got pokemon"
    return a

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
      ret = fn()
      if type(ret) == type(''): htmls.append(ret)
      else: htmls += ret

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
