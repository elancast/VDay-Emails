import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import datetime

from former import HtmlFormer
from former_v2 import HtmlFormerV2

V2_TEST = True

def getmsg(text, html):
  p1 = MIMEText(text, "plain")
  p2 = MIMEText(html, "html")
  msg = MIMEMultipart('alternative')
  msg.attach(p1)
  msg.attach(p2)
  return msg

def setMeta(msg, subject, to, fro, cc=None):
  msg['Subject'] = subject
  msg['From'] = fro
  msg['To'] = to
  addrs = [to]
  if cc != None: msg['CC'] = cc; addrs.append(cc)
  return addrs

def getSmtp(file, host="smtp.cs.princeton.edu", port=587):
  a = smtplib.SMTP(host, port)
  f = open(file, 'r')
  creds = map(lambda x: x.strip(), f.readlines())
  a.ehlo()
  a.starttls()
  a.login(creds[0], creds[1])
  return a

def getContent():
  if V2_TEST:
    former_v2 = HtmlFormerV2()
    return ('', former_v2.getHTML())
  else:
    former = HtmlFormer()
    return ('', former.getHtml())

def sendit(smtp, msg, subject, to, fro, cc=None):
  addrs = setMeta(msg, subject, to, fro, cc)
  s = msg.as_string()
  ret = smtp.sendmail(fro, addrs, s)
  print "Sent with return %s" % str(ret)

def getSubject():
  date = datetime.date.today().strftime('%a %b %d, %Y')
  return '[VDay emails] Happy %s!' % date

## TEST ##
cnt = getSmtp('/u/elancast/v/.shhhh')
(text, html) = getContent()
msg = getmsg(text, html)
to = "Rafrafiraf Romero <rromero@fb.com>"
megmil = "Emily Lancaster <elancast0421@gmail.com>"
me = "Emily Lancaster <elancast@cs.princeton.edu>"
subj = getSubject()
sendit(cnt, msg, subj, to, me, megmil)
