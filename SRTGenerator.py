'''
Texas A&M University - Spring 2014 - CSCE 438
HW3 - CrowdCaptioners

CrowdCaptioners Team:
Vishal Anand
Travis Purcell
Ricardo Zavala

File Created by: Travis Purcell, Ricardo Zavala

Purpose: Contains SRT caption file generation functions

'''

def GenerateSRT(title, duration, segment_length, video_start, video_end, Completed_HITs, Accepted_Answers):
    print "Generating SRT Caption File"
    SRTFile = open(title+".srt", 'w')
    captions = SortResults(Completed_HITs, Accepted_Answers)
    for i, caption in enumerate(captions):
        SRTFile.write(str(i+1)+"\n")
        SRTFile.write(ConvertSecondsToSRT(video_start[i])+" --> "+ConvertSecondsToSRT(video_end[i])+"\n")
        SRTFile.write(caption+"\n")
        SRTFile.write("\n")

    SRTFile.close()

#Sort the results, return a list of sorted answers
def SortResults(Completed_HITs, Accepted_Answers):
    sorted = []
    for i, item in enumerate(Completed_HITs):
        if Completed_HITs.count(item) > 1:
            Completed_HITs.pop(i)

    for i, item in enumerate(Completed_HITs):
        if Accepted_Answers[i][0] == item[0]:
            sorted.append(Accepted_Answers[i][1])
        else:
            for j, answer in enumerate(Accepted_Answers):
                if answer[0] == item[0]:
                    sorted.append(answer[1])
    print sorted
    return sorted

#Converts an integer to SRT readable timestamp
def ConvertSecondsToSRT(seconds):
    SRT_Time = ""
    #Hours
    if seconds >= 3600:
        if int(seconds/3600) < 10:
            SRT_Time += "0"+str(int(seconds/3600))
        else: SRT_Time += str(int(seconds/3600))
        while seconds >= 3600:
            seconds -= 3600
    else: SRT_Time += "00"
    SRT_Time += ":"

    #Minutes
    if seconds >= 60:
        if int(seconds/60) < 10:
            SRT_Time += "0"+str(int(seconds/60))
        else: SRT_Time += str(int(seconds/60))
        while seconds >= 60:
            seconds -= 60
    else: SRT_Time += "00"
    SRT_Time += ":"

    #Seconds
    if seconds > 0:
        if int(seconds) < 10:
            SRT_Time += "0"+str(int(seconds))
        else: SRT_Time += str(int(seconds))
    else: SRT_Time += "00"

    #Miliseconds (Not an issue using youtube implementation)
    SRT_Time += ",000"

    return SRT_Time
