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
import HITGeneration
import SRTGenerator
import CaptionAndValidate
import YouTube

#-------------------------------
#-------- Config Globals -------
#-------------------------------

#TODO Evaluated video length (20 seconds is too long, 5-10 seconds maybe)
embedded_video_length = 30;         #Embedded video length is n+1 watch time
video_start = []                    #Arrays of the sequential start and end times
video_end = []
embedded_urls = []

#Payment - Check HITGeneration.py config global

#TODO: Make assignmentNum 3, but impossible to test alone above 1
assignmentNum = 2                   #Number of times the videos will be captioned
validationNum = 1                   #Number of times the Caption HITs will validated

#-------------------------------
#------- Regular Globals -------
#-------------------------------

total_time = 0                         #Duration of embedded video - last segment is just remaining time of original video
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

YouTube.GetYouTubeData(url, total_time, embedded_video_length, embedded_urls, video_start, video_end, count)
count = len(embedded_urls)
total_time = video_end.pop()
video_end.append(total_time)

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

#TODO: Remove - DELETES ALL PREVIOUS USER HITS (Resets for testing...)
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

'''
    #TODO: Remove - DELETES ALL PREVIOUS USER HITS (Resets for testing...)
    Reset = mtc.get_all_hits()
    for hit in Reset:
    mtc.disable_hit(hit.HITId)
    print "Old HIT: " + hit.HITId + " - Disabled/Approved"
    '''

print "//////////////////// COMPLETED \\\\\\\\\\\\\\\\\\\\"