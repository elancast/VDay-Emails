import urllib
import time

MESSAGE = """
<table width="100%" cellpadding="0" cellspacing="0" bgcolor="B0C4DE"><tr><td>\n

<table bgcolor="white" cellpadding="0" style="font-family: Helvetica; margin-top: 12px; text-align: center;" width="650px" align="center">
<tr><td>
<br><br>
</td></tr>
<tr><td>
<h1 style="color:483D8B;">
<img height=30 src="http://i374.photobucket.com/albums/oo182/sikuljak/heart/th_red_heart.png">
Happy Email Time, Rafi!
<img height=30 src="http://i374.photobucket.com/albums/oo182/sikuljak/heart/th_red_heart.png">
</h1>
</td></tr>
<tr><td align="center">
<div style="width:500px; text-align:center;">
Hey Rafraf! If this is the first email you're seeing, then...
<br> <span style="color:red;"><b>Happy Valentine's Day</b></span>!<br><br>
This is going to be a daily email reminding you that I love youuu!
And it also attempts to update you on some of the things you enjoy, including aww reddit, xkcd, and puns.
Check it out! Today, and then tomorrow, and then the next day, and the next, and then forever after that!
Well, until I lose permission to hats...
<br><br>
I love you! Hope you enjoy!
<br><br>
UPDATE 2/17: Added National Geographic's photo of the day + r/pokemon. I still love you! Enjoy! &lt;3
<br><br>
UPDATE 6/11: Fixed XKCD. They took the transcript out of their HTML :(. Also link to imgur albums in r/zelda. Changed emails. Moved to CS server soak! :D
<br><br>
UPDATE 6/14: Hello <a href="https://github.com/elancast/VDay-Emails">github</a>. Added Flickr as a source of images. Still love you, Rafiiii!
</span>
</td></tr>
<tr><td>
<br><br>
</td></tr>
</table>

<table bgcolor="ffffff" cellpadding="12" style="font-family: Helvetica; margin-bottom:20px; margin-top: 12px;" width="324px" align="center">

<tr><td>
<br><br>
</td></tr>
"""

testhtml = """\
<html>
  <head></head>
  <body>
    <p>Hi!<br>
       How are you?<br>
       Here is the <a href="http://www.python.org">link</a> you wanted.<br>
<span style='font-family:"Courier New";'>
Here is an image:</span><br>
<img src='http://d21c.com/walpurgis9/happies/faces/004.gif'>
    </p>
<br><br><br><br><br>
<table>
<tr>
<td>hello</td>
<td> this is another column yea tables do yo thang</td>
</tr>
<tr>
<td>hello from row 2</td>
<td>nom nom nom</td>
</tr>
</table>
  </body>
</html>
"""

class HtmlFormer:
    def __init__(self, giveTest=True, grrr=True):
        self.html = testhtml
        self._formEmail()
        #self.html = "<b>Deprecated.</b> <i>This email does not properly capture Rafi's attention. As of 23 Apr 2012, the preferred way to do this is via a command-line program."

    def getHtml(self):
        return self.html

    def goToTheInternets(self, url, sleep=False):
        if sleep: time.sleep(3)
        return urllib.urlopen(url).read()

    def getFormattedTitle(self, text):
        st = 'color:#483D8B;'
        return '<h4 style="%s">%s</h4>' % (st, text)

    """ Returns XKCD html """
    def getXkcdHtml(self):
        url = "http://xkcd.com/"
        s = self.goToTheInternets(url)
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
            url = 'http://xkcd.com'

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
            img = '<a href="%s"><img src="%s" title="%s" width=300 /></a>' % (url, url, title)
            if len(x) > 3 and x[3]:
                img = img.replace('img src', 'a href')
                img = img.replace('/>', '>Check out the imgur album!</a>')
            descr = 'Read Reddit\'s take on this image <a href="%s">here</a>.<br><br>' % reddit
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
            time.sleep(10)
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
        url = "http://feeds.feedburner.com/bingimages"
        s = self.goToTheInternets(url)
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

            # Image link
            tag = 'enclosure url="'
            start = part.index(tag) + len(tag)
            end = part.index('"', start)
            url = part[start : end]

            # HTML!
            bing = '"http://www.bing.com/"'
            title = self.getFormattedTitle('Today\'s Bing picture is...')
            print 'got bing'
            return '%s<a href=%s><img src="%s" width=300 title="%s" /></a>' \
                % (title, bing, url, desc)
        return ''

    def getAstronomyVideoThoseFuckers(self, s):
        tag = '<iframe '
        if not tag in s: return None
        start = s.index(tag)
        start = s.index('http', start)
        end = s.index('"', start)
        return (s[start:end], end)

    def getAstronomy(self):
        url = 'http://apod.nasa.gov/apod/'; tag = 'IMG SRC="'
        s = self.goToTheInternets(url)

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
            if not 'http://' in url: url = 'http://apod.nasa.gov/apod/' +url

        # Get the description
        tag = '<b>'
        start = s.index(tag, end) + len(tag)
        end = s.index('<', start)
        descr = s[start : end].strip()

        # Get the date
        start = s.index('?date=') + len('?date=')
        end = s.index('"', start)
        date = s[start : end]
        perma = 'http://apod.nasa.gov/apod/ap%s.html' % date

        # Do it!
        start = self.getFormattedTitle('Today\'s Astronomy Picture of the Day is...')
        if not vid:
            img = '<a href="%s"><img src="%s" title="%s" width=300 /></a>' % \
                  (perma, url, descr)
        else:
            img = '<a href="%s">%s</a>' % (url, descr)
        print 'got astronomy'
        return start + img

    """ Returns a pun from a daily pun site """
    def getPun(self):
        url = 'http://feeds.feedburner.com/PunOfTheDay'
        s = self.goToTheInternets(url)
        s = s[s.index('<item>'):]
        tag = '<description>'
        start = s.index(tag) + len(tag)
        end = s.index('&lt;', start)
        pun = s[start : end]
        msg = 'Puns stolen from <a href="http://www.punoftheday.com/">Pun of the Day</a>.'
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
        url = 'http://photography.nationalgeographic.com/photography/photo-of-the-day/'
        s = self.goToTheInternets(url)
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
        it = '<a href="%s"><img src="%s" title="%s" width=300 /></a>' % (img, img, caption)
        return '%s%s<br><br>%s' % (title, caption, it)

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
        html = MESSAGE

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

