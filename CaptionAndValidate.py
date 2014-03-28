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
import time
import HITGeneration
import difflib
import wx

#-------------------------------
#------- Config Globals --------
#-------------------------------
validationHurdle = 0.95             #Requires that answers be this similar [0,1] to be considered the same

#Evaluates similarity of two strings and returns a bool
def similar(string1, string2, hurdle):
    return difflib.SequenceMatcher(a=string1.lower(), b=string2.lower()).ratio() > hurdle

#Get all HITs that have all assignments completed
def get_all_reviewable_hits(mtc):
    #-------------------------------
    #-------- Gather Results -------
    #-------------------------------
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


#By FAR the most time consuming function
#Returns a list of validated answers
def CaptionAndValidationLoop(dlg,mtc, HIT_IDs, count, assignmentNum, embedded_urls, Completed_HITs, Accepted_Answers):
    #-------------------------------
    #--------- Holding Loop --------
    #-------------------------------
    #dlg = wx.GenericProgressDialog("test", "test", maximum=count, parent=None,
    #                        style=wx.PD_AUTO_HIDE|wx.PD_APP_MODAL)
    #dlgcount = 10
    TOTAL_HITS = count
      
    Validation_HIT_Count = 0    #Number of validation hits generated
    print "Count = " + str(count)
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
        valid = False
        for hit in hits:
            mtc.set_reviewing(hit.HITId)
            HIT_Answers = []
            assignments = mtc.get_assignments(hit.HITId)
            for assignment in assignments:
                print "Worker ID:"+assignment.WorkerId+"\nAssignment ID: "+assignment.AssignmentId+"\nHIT ID: " + hit.HITId
                for question_form_answer in assignment.answers[0]:
                    #try:
                    #    for key, value in question_form_answer.fields:
                    #        HIT_Answers.append(value)
                    #        print "%s - %s" % (key,value)
                    #except:
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
                        if similar(a1, a2, validationHurdle):
                            similarity += validationHurdle;
                #If the responses are the same or they are similar enough then accept the 1st response
                if perfectAnswers or (similarity/(assignmentNum*assignmentNum)) > validationHurdle:
                    print "Passed Validation Hurdle... No Validation HIT generated..."
                    mtc.approve_assignment(assignment.AssignmentId)
                    valid = True
                    Accepted_Answers.append((hit.HITId, HIT_Answers[0]))
                    #mtc.disable_hit(hit.HITId)
                else:
                    #TODO: If the captions are not similar enough
                    embedded_url = embedded_urls[HIT_IDs.index(hit.HITId)]
                    ValidationID = HITGeneration.GenerateValidationHIT(mtc, HIT_Answers, embedded_url)
                    print "ValidationHitID = "+ ValidationID
                    HITId_and_ValidationID = (hit.HITId, ValidationID)
                    Validation_HIT_Count += 1
                    #mtc.disable_hit(hit.HITId)
                    #mtc.approve_assignment(assignment.AssignmentId)
                print "_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_"
            if valid:
                Completed_HITs.append((hit.HITId, "NONE"))
            else:
                    Completed_HITs.append(HITId_and_ValidationID)
            count -= 1 #Got the result from a video segment HIT (regardless of validation it happened)
            #mtc.dispose_hit(hit.HITId)
            mtc.set_reviewing(hit.HITId)
            #updateString = "Video Segments Remaining: %d of %d" (count,TOTAL_HITS)
            wx.CallAfter(dlg.Update,1,"Loading...")


    print "Count = " + str(count)
    print "---------------- NO MORE CAPTION HITS TO FIND -----------------------"
    print Completed_HITs
        
    #-------------------------------
    #--- Validation Holding Loop ---
    #-------------------------------
    #By this time all validation HITs have been generated (if any)
    wx.CallAfter(dlg.Update,0,"Validating and Generating .srt File")
    RedoCationHITs = []

    while Validation_HIT_Count > 0 and count == 0:
        print "Validation Count = " + str(count)
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
                    #try:
                    #    for key, value in question_form_answer.fields:
                    #        HIT_Answers.append(value)
                    #        print "%s - %s" % (key,value)
                    #except:
                        for value in question_form_answer.fields:
                            HIT_Answers.append(value)
                            print value

                #TODO: Modify HIT_Answers[0] based on the desgin implementation (int, str, etc... as well as indicies)... 
                #Do a search/replace to be sure
                #Check if the answer is the "None of the above" choice
                if HIT_Answers[0] == "None of the Above":
                    HITId = HITGeneration.GenerateCaptionHIT(mtc, 1, assignmentNum, embedded_urls)[0]
                    RedoCationHITs.append(HITId)
                    #mtc.approve_assignment(assignment.AssignmentId)

                    #Remove the assignment from completed list since it failed and has to be recreated
                    removing = [i for i, v in enumerate(Completed_HITs) if v[0] == hit.HITId]
                    Completed_HITs.pop(removing[0])

                else:
                    Accepted_Answers.append((hit.HITId, HIT_Answers[0]))

                print "_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_"
        Validation_HIT_Count -= 1   #Got the result from a video segment HIT (regardless of validation it happened)
                #mtc.approve_assignment(assignment.AssignmentId)
                #mtc.disable_hit(hit.HITId)  #Disable hit regardless

    if len(RedoCationHITs) > 0:
        CaptionAndValidationLoop(dlg,mtc, RedoCationHITs, len(RedoCationHITs), assignmentNum, embedded_urls, Completed_HITs, Accepted_Answers)

    wx.CallAfter(dlg.Destroy)
