'''
Texas A&M University - Spring 2014 - CSCE 438
HW3 - CrowdCaptioners

CrowdCaptioners Team:
Vishal Anand
Travis Purcell
Ricardo Zavala

File Created by: Travis Purcell

Purpose: Contains the main loop of the program
'''
#-------------------------------
# ----------- Import -----------
#-------------------------------

from boto.mturk.connection import MTurkConnection
import simplejson as json
import requests
import urllib2
import re
import HITGeneration
import SRTGenerator
import GUI
import CaptionAndValidate

#-------------------------------
#-------- Config Globals -------
#-------------------------------

#TODO Evaluated video length (20 seconds is too long, 5-10 seconds maybe)
embedded_video_length = 20;         #Embedded video length is n+1 watch time
video_start = []                    #Arrays of the sequential start and end times
video_end = []

#Payment - Check HITGeneration.py config global

#TODO: Make assignmentNum 3, but impossible to test alone above 1
assignmentNum = 1                   #Number of times the videos will be captioned
validationNum = 1                   #Number of times the Caption HITs will validated

#-------------------------------
#------- Regular Globals -------
#-------------------------------

seconds = 0                         #Duration of embedded video - last segment is just remaining time of original video
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

#total_time = int(data_duration)     #duration of original video
total_time = 60
while (seconds < total_time):       #Build the start and end arrays
     video_start.append(seconds)
     seconds+=embedded_video_length-1
     if seconds+1 < total_time and seconds < total_time:
        video_end.append(seconds)
     else:
        video_end.append(seconds+1)
     count+=1
     seconds+=1

time_left = total_time-(embedded_video_length*int(total_time/embedded_video_length))
print time_left
if time_left < embedded_video_length and time_left > 0:
    start = video_start.pop()
    print start
    video_start.append(start)
    video_end.pop()
    video_end.append(start + time_left)

#Build Embedded URL list
embedded_urls = []
for i in range(0, count):
    embedded_urls.append("http://www.youtube.com/embed/"+Video_ID+"?autoplay=1&amp;modestbranding=1&amp;iv_load_policy=3&amp;showinfo=0&amp;rel=0&amp;start="+str(video_start[i])+"&amp;end="+str(video_end[i]))

print embedded_urls
count = len(embedded_urls)

#-------------------------------
#-------- AWS Connection -------
#-------------------------------

ACCESS_ID = raw_input("ACCESS_ID: ")
SECRET_KEY = raw_input("SECRET_KEY: ");
#TODO: Change from sandbox when live
HOST = 'mechanicalturk.sandbox.amazonaws.com'

mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)

#TODO: Remove?
print mtc.get_account_balance() 

#TODO: Remove? - DELETES ALL PREVIOUS USER HITS (Resets for testing...)
Reset = mtc.get_all_hits()
for hit in Reset:
    mtc.disable_hit(hit.HITId)
    print "Old HIT: " + hit.HITId + " - Disabled"

#-------------------------------
#-------- HIT Generation -------
#-------------------------------

HIT_IDs = HITGeneration.GenerateCaptionHIT(mtc, count, assignmentNum, embedded_urls)


Completed_HITs = []         #Used to link caption and validation HITs
Accepted_Answers = []       #Used to build the SRT File

CaptionAndValidate.CaptionAndValidationLoop(mtc, HIT_IDs, count, assignmentNum, embedded_urls, Completed_HITs, Accepted_Answers)

print "Completed Hits: " 
print Completed_HITs
print "Accepted Answers: "
print Accepted_Answers

SRTGenerator.GenerateSRT(data_title, total_time, embedded_video_length, video_start, video_end, Completed_HITs, Accepted_Answers)

print "//////////////////// COMPLETED \\\\\\\\\\\\\\\\\\\\"