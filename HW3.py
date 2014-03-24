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
import simplejson as json
import requests
import urllib2
import re
import time
import HITGeneration

#-------------------------------
#-------- Config Globals -------
#-------------------------------

#TODO: Need to find them in the file again...

seconds = 0                         #duration of embedded video - last segment is just remaining time of original video
embedded_video_length = 20;         #embedded video length is n+1 watch time
video_start = []                    #arrays of the sequential start and end times
video_end = []
validationHurdle = 0.95             #Requires that answers be this similar [0,1] to be considered the same

#TODO: Make it 3, but impossible to test alone above 1
assignmentNum = 1                   #Number of times the videos will be captioned
validationNum = 1                   #Number of times the Caption HITs will validated

#-------------------------------
#------- Regular Globals -------
#-------------------------------

count = 0                           #number of video segments (aka HITs)

#-------------------------------
#----------- YouTube -----------
#-------------------------------

#Test URL - Standard
url = "http://www.youtube.com/watch?v=KaqC5FnvAEc"
#Test URL - Compelex
#url = "http://www.youtube.com/watch?v=b19l1y7h8XA&list=PLU3TaPgchJtS0U_Qd_bEB5GxAZ4C4_pId"
#Test URL - Invalid
#url = "http://www.bob.com/watch?v=XXXXXXXXX"
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

total_time = int(data_duration)     #duration of original video
while (seconds < total_time):       #Build the start and end arrays
     video_start.append(seconds)
     seconds+=embedded_video_length-1
     video_end.append(seconds)
     count+=1
     seconds+=1

#Build Embedded URL list
embedded_urls = []
for i in range(0,count):
    embedded_urls.append("http://www.youtube.com/embed/"+Video_ID+"?autoplay=1&amp;modestbranding=1&amp;iv_load_policy=3&amp;showinfo=0&amp;rel=0&amp;start="+str(video_start[i])+"&amp;end="+str(video_end[i]))

print embedded_urls
count = len(embedded_urls)

#-------------------------------
#-------- AWS Connection -------
#-------------------------------

ACCESS_ID = raw_input("ACCESS_ID: ")
SECRET_KEY = raw_input("SECRET_KEY: ");
HOST = 'mechanicalturk.sandbox.amazonaws.com'

mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)

#TODO: Remove?
print mtc.get_account_balance() 

#TODO: Remove - DELETES ALL USER HITS (Resets for testing...)
Reset = mtc.get_all_hits()
for hit in Reset:
    mtc.disable_hit(hit.HITId)
    print hit.HITId + " - Disabled"

#-------------------------------
#-------- HIT Generation -------
#-------------------------------

HIT_IDs = HITGeneration.GenerateCaptionHIT(mtc, count, assignmentNum, embedded_urls)

#-------------------------------
#-------- Gather Results -------
#-------------------------------

#Get all HITs that have all assignments completed
def get_all_reviewable_hits(mtc):
    page_size = 50
    hits = mtc.get_reviewable_hits(page_size=page_size)
    print "Total results to fetch %s " % hits.TotalNumResults
    #print "Request hits page %i" % 1
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

#-------------------------------
#--------- Holding Loop --------
#-------------------------------

Completed_HITs = []         #Used to link caption and validation HITs
Validation_HIT_Count = 0    #Number of validation hits generated
while count > 0:
    hits = []
    while hits == []:
        hits = get_all_reviewable_hits(mtc)
        if hits == []:
            time.sleep(30)  #Wait for a bit...
        #print hits
    print "---------------- HIT(s) Reviewable -----------------------"
    
    #Design Notes:
    #So.... A hit has had all it's assignments completed... but I can't see multiple assignments myself because I can't do them all... 
    #so I have to guess how to get assignment data is organized and how to put it back in the correct order after verification...
    #....
    #assignment in assignments values into list, compare items in list (same or similar = good), develope new HIT for validation,
    #tie new validation HIT to old video segment HIT
    #pay workers based on some security question and some form of valid entry in text field - OR - security questions and validation results
    #loop as needed

    for hit in hits:
        HIT_Answers = []
        assignments = mtc.get_assignments(hit.HITId)
        for assignment in assignments:
            print "Worker ID:"+assignment.WorkerId+"\nAssignment ID: "+assignment.AssignmentId+"\nHIT ID: " + hit.HITId
            for question_form_answer in assignment.answers[0]:
                try:
                    for key, value in question_form_answer.fields:
                        HIT_Answers.append(value)
                        print "%s - %s" % (key,value)
                except:
                    for value in question_form_answer.fields:
                        HIT_Answers.append(value)
                        print value

            #-------------------------------
            #------- Similarity Check ------
            #-------------------------------
            similarity = 0
            perfectAnswers = False
            perfectAnswer = ""
            #if assignmentNum > 1:
            for a1 in HIT_Answers:
                #Check if all answers match
                print HIT_Answers
                if HIT_Answers.count(a1) == assignmentNum:
                    print "Count of a1: " + str(HIT_Answers.count(a1))
                    print "--- !!! Total Validation !!! ---"
                    perfectAnswers = True
                    perfectAnswer = a1
                    break
                #Otherwise, check how similar the answers
                for a2 in HIT_Answers:
                    if HITGeneration.similar(a1, a2, validationHurdle):
                        similarity += validationHurdle;
            #If the responses are the same or they are similar enough then accept the 1st response
            if perfectAnswers or (similarity/(assignmentNum*assignmentNum)) > validationHurdle:
                print "Passed Validation Hurdle... No Validation HIT generated..."
                mtc.approve_assignment(assignment.AssignmentId)
                Completed_HITs.append((hit.HITId, "NONE"))
                mtc.disable_hit(hit.HITId)
            else:
                embedded_url = embedded_urls[HIT_IDs.index(hit.HITId)]
                ValidationID = HITGeneration.GenerateValidationHIT(mtc, HIT_Answers, embedded_url)
                HITId_and_ValidationID = (hit.HITId, ValidationID)
                Validation_HIT_Count += 1
                Completed_HITs.append(HITId_and_ValidationID)
                mtc.disable_hit(hit.HITId)
            print "_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_"
            count -= 1 #Got the result from a video segment HIT (regardless of validation it happened)
            

print "---------------- NO MORE CAPTION HITS TO FIND -----------------------"
print Completed_HITs

#-------------------------------
#--- Validation Holding Loop ---
#-------------------------------

'''
#By this time all validation HITs have been generated (if any)
while Validation_HIT_Count > 0:
    validation_hits = []
    while validation_hits == []:
        validation_hits = get_all_reviewable_hits(mtc)
        if validation_hits == []:
            time.sleep(30)  #Wait for a bit...
        #print hits
    print "----------- Validation HIT(s) Reviewable ------------------"

    for hit in validation_hits:
        HIT_Answers = []
        print hit.HITId
        assignments = mtc.get_assignments(hit.HITId)
        for assignment in assignments:
            print "Worker ID:"+assignment.WorkerId+"\nValidation Assignment ID: "+assignment.AssignmentId+"\nHIT ID: " + hit.HITId
            for question_form_answer in assignment.answers[0]:
                try:
                    for key, value in question_form_answer.fields:
                        HIT_Answers.append(value)
                        print "%s - %s" % (key,value)
                except:
                    for value in question_form_answer.fields:
                        HIT_Answers.append(value)
                        print value

            #-------------------------------
            #------- Similarity Check ------
            #-------------------------------
            similarity = 0
            perfectAnswers = False
            perfectAnswer = ""
            #if validationNum > 1:
            for a1 in HIT_Answers:
                #Check if all answers match
                if HIT_Answers.count(a1) == assignmentNum:
                    print "--- !!! Total Validation !!! ---"
                    perfectAnswers = true
                    perfectAnswer = a1
                    break
                #Otherwise, check how similar the answers
                for a2 in HIT_Answers:
                    if similar(a1, a2, validationHurdle):
                        similarity += validationHurdle;
            #If the responses are the same or they are similar enough then accept the 1st response
            if perfectAnswers or (similarity/(assignmentNum*assignmentNum)) > validationHurdle:
                print "Accept without any validation HIT"
                print "Accept First Answer (since they are so similar)"
                mtc.approve_assignment(assignment.AssignmentId)
                Completed_HITs.append((hit.HITId, perfectAnswer))
                mtc.disable_hit(hit.HITId)
            else:
                HITId_and_ValidationID = (hit.HITId, GenerateValidationHIT(mtc, HIT_Answers))
                Validation_HIT_Count += 1
                Completed_HITs.append(HITId_and_ValidationID)

            print "_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_"
            Validation_HIT_Count -= 1 #Got the result from a video segment HIT (regardless of validation it happened)
            mtc.disable_hit(hit.HITId)
'''
