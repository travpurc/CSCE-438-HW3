'''
Texas A&M University - Spring 2014 - CSCE 438
HW3 - CrowdCaptioners

CrowdCaptioners Team:
Vishal Anand
Travis Purcell
Ricardo Zavala

File Created by: Travis Purcell
'''
#-------------------------------
# ----------- Import -----------
#-------------------------------

from boto.mturk.connection import MTurkConnection
from boto.mturk.question import QuestionContent,Question,QuestionForm,Overview,AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer
import simplejson as json
import requests
import urllib2
import re

#-------------------------------
#----------- YouTube -----------
#-------------------------------

#Test URL - Standard
url = "http://www.youtube.com/watch?v=KaqC5FnvAEc"
#Test URL - Compelex
#url = "http://www.youtube.com/watch?v=b19l1y7h8XA&list=PLU3TaPgchJtS0U_Qd_bEB5GxAZ4C4_pId"
#Test URL - Invalid
url = "http://www.bob.com/watch?v=XXXXXXXXX"
#Test URL - IS NOT EMBEDDABLE and CAN'T BE KNOWN PRIOR TO ATTEMPTING TO PLAY THE VIDEO
#TODO: Generate embedded link and make user manually check first...
#url = "http://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Get the YouTube link from user
#url = raw_input("Youtube Link: ")

try:
    Video_ID = re.search( "v=(.*)&|v=(.*)", url)
    if Video_ID.group(1) == None:
        Video_ID = Video_ID.group(2)
    else:
        Video_ID = Video_ID.group(1)
except:
    print "Invalid Youtube Url"
    quit(0)


Video_Data = "https://gdata.youtube.com/feeds/api/videos/"+Video_ID+"?v=2"

#print Video_Data

#Try to get a response from the provided url
try:
    data = (urllib2.urlopen(Video_Data)).read()
except urllib2.HTTPError as e:
    print 'The server couldn\'t fulfill the request.'
    print 'HTTP Error code: ', e.code
    quit(0)
except urllib2.URLError as e:
    print 'We failed to reach YouTube server.'
    print 'Reason: ', e.reason
    quit(0)

#Print the response
#print data

data_title = re.search( "<title>(.*)</title>", data).group(1)
print "Title: "+ data_title

#Catchable errors on embedding the video...
error = re.search( "yt:state name='([a-bA-B]*)'", data)
print error
if error != None:
    if error.group(1) == "resricted" or error.group(1) == "rejected":
        print "Error: Video "+ error.group(1) +" by YouTube, unable to generate caption..."
    else:
        print "Error: Video failed, unable to generate caption..."
    quit(0)

data_duration = re.search( "duration='([0-9]*)'", data).group(1)
print "Duration: "+ data_duration
data_embeddable = re.search( "action='embed' permission='([a-z]*)'", data).group(1)
print "Embeddable: "+ data_embeddable
if data_embeddable != "allowed":
    print "Error: Video is not currently allowed to be embedded, unable to generate captions..."
    quit(0)

#-------------------------------
#-------- Embedded Video -------
#-------------------------------

seconds = 0                         #duration of embedded video - last segment is just remaining time of originak video
embedded_video_length = 20;         #embedded video length is n+1 watch time
total_time = int(data_duration)     #duration of original video
count = 0                           #number of video segments  
video_start = []                    #arrays of the sequential start and end times
video_end = []
while (seconds < total_time):       #Build the start and end arrays
     video_start.append(seconds)
     seconds+=embedded_video_length-1
     video_end.append(seconds)
     count+=1
     seconds+=1

#Build Embedded URL list
embedded_url = []
for i in range(0,count):
    embedded_url.append("http://www.youtube.com/embed/"+Video_ID+"?autoplay=1&modestbranding=1&iv_load_policy=3&showinfo=0&rel=0&start="+str(video_start[i])+"&end="+str(video_end[i]))

print embedded_url

#-------------------------------
#------------ MTURK ------------
#-------------------------------
'''
ACCESS_ID = raw_input("ACCESS_ID: ")
SECRET_KEY = raw_input("SECRET_KEY: ");
HOST = 'mechanicalturk.sandbox.amazonaws.com'

mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)

print mtc.get_account_balance() 


title = 'Give your opinion about a website'
description = ('Visit a website and give us your opinion about'
               ' the design and also some personal comments')
keywords = 'website, rating, opinions'
 
ratings =[('Very Bad','-2'),
         ('Bad','-1'),
         ('Not bad','0'),
         ('Good','1'),
         ('Very Good','1')]
 
#---------------  BUILD OVERVIEW -------------------
 
overview = Overview()
overview.append_field('Title', 'Give your opinion on this website')
overview.append(FormattedContent('<a target="_blank"'
                                 ' href="http://www.toforge.com">'
                                 ' Mauro Rocco Personal Forge</a>'))
 
#---------------  BUILD QUESTION 1 -------------------
 
qc1 = QuestionContent()
qc1.append_field('Title','How looks the design ?')
 
fta1 = SelectionAnswer(min=1, max=1,style='dropdown',
                      selections=ratings,
                      type='text',
                      other=False)
 
q1 = Question(identifier='design',
              content=qc1,
              answer_spec=AnswerSpecification(fta1),
              is_required=True)
 
#---------------  BUILD QUESTION 2 -------------------
 
qc2 = QuestionContent()
qc2.append_field('Title','Your personal comments')
 
fta2 = FreeTextAnswer()
 
q2 = Question(identifier="comments",
              content=qc2,
              answer_spec=AnswerSpecification(fta2))
 
#--------------- BUILD THE QUESTION FORM -------------------
 
question_form = QuestionForm()
question_form.append(overview)
question_form.append(q1)
question_form.append(q2)
 
#--------------- CREATE THE HIT -------------------
 
new_hit = mtc.create_hit(questions=question_form,
               max_assignments=1,
               title=title,
               description=description,
               keywords=keywords,
               duration = 60*5,
               reward=0.05)


'''

'''
HIT Data Structure

<HIT>
  <HITId>123RVWYBAZW00EXAMPLE</HITId>
  <HITTypeId>T100CN9P324W00EXAMPLE</HITTypeId> - The Website ID
  <CreationTime>2005-06-30T23:59:59</CreationTime>
  <HITStatus>Assignable</HITStatus>
  <MaxAssignments>5</MaxAssignments>
  <AutoApprovalDelayInSeconds>86400</AutoApprovalDelayInSeconds>
  <LifetimeInSeconds>86400</LifetimeInSeconds>
  <AssignmentDurationInSeconds>300</AssignmentDurationInSeconds>
  <Reward>
    <Amount>25</Amount>
    <CurrencyCode>USD</CurrencyCode>
    <FormattedPrice>$0.25</FormattedPrice>
  </Reward>
  <Title>Location and Photograph Identification</Title>
  <Description>Select the image that best represents...</Description>
  <Keywords>location, photograph, image, identification, opinion</Keywords>
  <Question>
    &lt;QuestionForm&gt;
      [XML-encoded Question data]
    &lt;/QuestionForm&gt;
  </Question>
  <QualificationRequirement>
    <QualificationTypeId>789RVWYBAZW00EXAMPLE</QualificationTypeId>
    <Comparator>GreaterThan</Comparator>
    <Value>18</Value>
  </QualificationRequirement>
  <HITReviewStatus>NotReviewed</HITReviewStatus>
</HIT>

print new_hit[0].HITId
print new_hit[0].HITTypeId
'''

'''
def get_all_reviewable_hits(mtc):
    page_size = 50
    hits = mtc.get_reviewable_hits(page_size=page_size)
    print "Total results to fetch %s " % hits.TotalNumResults
    print "Request hits page %i" % 1
    total_pages = float(hits.TotalNumResults)/page_size
    int_total= int(total_pages)
    if(total_pages-int_total>0):
        total_pages = int_total+1
    else:
        total_pages = int_total
    pn = 1
    while pn < total_pages:
        pn = pn + 1
        print "Request hits page %i" % pn
        temp_hits = mtc.get_reviewable_hits(page_size=page_size,page_number=pn)
        hits.extend(temp_hits)
    return hits

hits = get_all_reviewable_hits(mtc)
 
for hit in hits:
    assignments = mtc.get_assignments(hit.HITId)
    for assignment in assignments:
        print "Answers of the worker %s" % assignment.WorkerId
        for question_form_answer in assignment.answers[0]:
            for key, value in question_form_answer.fields:
                print "%s: %s" % (key,value)
        print "--------------------"
'''