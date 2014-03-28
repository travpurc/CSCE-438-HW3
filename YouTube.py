'''
Texas A&M University - Spring 2014 - CSCE 438
HW3 - CrowdCaptioners

CrowdCaptioners Team:
Vishal Anand
Travis Purcell
Ricardo Zavala

File Created by: Travis Purcell

Purpose: Contains HIT and Validation Loop Functions
'''

#-------------------------------
# ----------- Import -----------
#-------------------------------
import requests
import urllib2
import re

#Fills in key data for the main program
def GetYouTubeData(url, embedded_video_length, embedded_urls, video_start, video_end):
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
    seconds = 0
    total_time = int(data_duration)     #duration of original video
    count = 0
    #total_time = 60
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
    if time_left < embedded_video_length and time_left > 0:
        start = video_start.pop()
        video_start.append(start)
        video_end.pop()
        video_end.append(start + time_left)

    #Build Embedded URL list
    #embedded_urls = []
    for i in range(0, count):
        embedded_urls.append("http://www.youtube.com/embed/"+Video_ID+"?autoplay=1&amp;modestbranding=1&amp;iv_load_policy=3&amp;showinfo=0&amp;rel=0&amp;start="+str(video_start[i])+"&amp;end="+str(video_end[i]))