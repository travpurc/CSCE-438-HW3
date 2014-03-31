'''
Texas A&M University - Spring 2014 - CSCE 438
HW3 - CrowdCaptioners

CrowdCaptioners Team:
Vishal Anand
Travis Purcell
Ricardo Zavala

File Created by: Travis Purcell, Ricardo Zavala

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
validationHurdle = 0.85             #Requires that answers be this similar [0,1] to be considered the same

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
        #print "Request hits page %i" % pn
        temp_hits = mtc.get_reviewable_hits(page_size=page_size,page_number=pn)
        hits.extend(temp_hits)
    return hits

def find_position(hit_id, completed_hits):
    r = 0
    was_found = False
    can_continue = True
    while not was_found: 
        if not can_continue: break
        current_id = completed_hits[r][0]
        print hit_id
        print current_id
        was_found = hit_id == current_id
        r += 1
        if r == len(completed_hits):
            can_continue = False
    if was_found:
        return r
    print "\n---Shouldn't be here!!---\n"
    return -1

def make_direct_validation_hit(hit_id, completed_hits, urls):
    #TODO
    #read hit id, find its position in completed_hits (/2)
    #and extract that url to generate NEW (not validation) hit
    #update completed hit with new hitID   
    pass

def make_validation_hit(mtc, options, url):
    return HITGeneration.GenerateValidationHIT(mtc, options, url)

def check_results(mtc, completed_hits, hit_ids, urls):
    answers = []
    hits_available = get_all_reviewable_hits(mtc)
    for hit in hits_available:
        mtc.set_reviewing(hit.HITId)
        hit_id = hit.HITId
        assignments = mtc.get_assignments(hit_id)
        temp = []
        for assignment in assignments:
            for question_form_answer in assignment.answers[0]:
                r = 0
                for answer in question_form_answer.fields:
                    #print answer
                    if r == 0:
                        if answer != '1':
                            print "incorrect security answer"
                            hit_id = make_direct_validation_hit(hit_id, completed_hits, urls)
                            temp[0] = [hit_id, ""]
                            r += 2
                            continue
                        else:
                            r += 1
                    elif r == 1:
                        temp[0] = [hit_id, answer]
                    elif r == 2:
                        continue
                    else:
                        print "Why am I here?"
                        continue
                # End first for
            answers.append(temp)
            # End second for
    answers = validate(answers, completed_hits, mtc, hit_ids, urls)
    return answers

def validate(answers, completed_hits, mtc, hit_ids, urls):
    valid_answers = []
    for assignment in answers:
        r = 0
        s = 1
        id_r = assignment[r][0]
        if id_r == "":
            continue
        if len(assignment) > 2: # There were repeats... Compare 1 and 3
            s += 1
        id_s = assignment[s][0]
        answer1 = assignment[r][1]
        answer2 = assignment[s][1]
        # This should not happen, except after an invalid security answer:
        t = find_position(id_r, completed_hits)
        u = t
        if id_r != id_s:
            u = find_position(id_s, completed_hits)
        if similar(answer1, answer2, validationHurdle):
            valid_answers.append([u/2, answer1])
        else:
            make_validation_hit(mtc, [answer1, answer2], urls[hit_ids.index(id_r)])
    return valid_answers

def merge_answers(captions, accepted_answers):
    for r in captions:
        print "Captions:"
        print captions
        print "Accepted answers before:"
        print accepted_answers
        accepted_answers[r[0]] = r[1]
        print "Accepted answers after:"
        print accepted_answers
    return len(captions)*2

#By FAR the most time consuming function
#Returns a list of validated answers
def CaptionAndValidationLoop(dlg, mtc, HIT_IDs, count, assignmentNum, embedded_urls, Completed_HITs, Accepted_Answers):
    total_hits = count*assignmentNum
    hits_remaining = total_hits
    while hits_remaining > 0:
        captions = check_results(mtc, Completed_HITs, HIT_IDs, embedded_urls)
        valid_answers = merge_answers(captions, Accepted_Answers)
        print valid_answers
        if valid_answers > 0:
            hits_remaining -= valid_answers
        else:
            print Accepted_Answers
            time.sleep(30)
    
    #-------------------------------
    #--------- Holding Loop --------
    #-------------------------------
    #dlg = wx.GenericProgressDialog("test", "test", maximum=count, parent=None,
    #                        style=wx.PD_AUTO_HIDE|wx.PD_APP_MODAL)
    #dlgcount = 10
'''    TOTAL_HITS = count

    Validation_HIT_Count = 0    #Number of validation hits generated
    RedoCaptionHITs = []
    print "Count = " + str(count)
    invalidCaption = False
    invalidHit = ""
    while count > 0:
        hits = []
        while hits == []:
            hits = get_all_reviewable_hits(mtc)
            if hits == []:
                time.sleep(30)  #Wait for a bit...
            #print hits
        print "---------------- HIT(s) Reviewable -----------------------"
        valid = False
        for hit in hits:
            mtc.set_reviewing(hit.HITId)
            HIT_Answers = []
            assignments = mtc.get_assignments(hit.HITId)
            for assignment in assignments:
                print "Worker ID:"+assignment.WorkerId+"\nAssignment ID: "+assignment.AssignmentId+"\nHIT ID: " + hit.HITId
                for question_form_answer in assignment.answers[0]:
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
                for i in range(0, len(HIT_Answers), 2):
                    if HIT_Answers[i] != '1':
                        print "WARNING: Invalid Caption Security Question Answer Detected... "
                        invalidCaption = True
                        invalidHit = hit.HITId
                        break
                    #Check if all answers match
                    print HIT_Answers
                    if HIT_Answers.count(HIT_Answers[i+1]) == assignmentNum:
                        print "Count of a1: " + str(HIT_Answers.count(HIT_Answers[i+1]))
                        print "--- !!! Total Validation !!! ---"
                        perfectAnswers = True
                        perfectAnswer = HIT_Answers[i+1]
                        break
                    #Otherwise, check how similar the answers
                    for j in range(0, len(HIT_Answers), 2):
                        if similar(HIT_Answers[i+1], HIT_Answers[j+1], validationHurdle):
                            similarity += validationHurdle;
                if invalid: break
                #If the responses are the same or they are similar enough then accept the 1st response
                elif perfectAnswers or (similarity/(assignmentNum*assignmentNum)) > validationHurdle:
                    print "Passed Validation Hurdle... No Validation HIT generated..."
                    mtc.approve_assignment(assignment.AssignmentId)
                    valid = True
                    Accepted_Answers.append((hit.HITId, HIT_Answers[0]))
                    #mtc.disable_hit(hit.HITId)
                    #mtc.set_reviewing(hit.HITId)
                else:
                    #TODO: If the captions are not similar enough
                    embedded_url = embedded_urls[HIT_IDs.index(hit.HITId)]
                    ValidationID = HITGeneration.GenerateValidationHIT(mtc, HIT_Answers, embedded_url)
                    print "ValidationHitID = "+ ValidationID
                    HITId_and_ValidationID = (hit.HITId, ValidationID)
                    Validation_HIT_Count += 1
                    #mtc.disable_hit(hit.HITId)
                    #mtc.approve_assignment(assignment.AssignmentId)
                    #mtc.set_reviewing(hit.HITId)
                print "_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_"
            if invalidCaption: break
            elif valid: Completed_HITs.append((hit.HITId, "NONE"))
            else: Completed_HITs.append(HITId_and_ValidationID)
            count -= 1 #Got the result from a video segment HIT (regardless of validation it happened)
            #mtc.dispose_hit(hit.HITId)
            #updateString = "Video Segments Remaining: %d of %d" (count,TOTAL_HITS)
            wx.CallAfter(dlg.Update,1,"Loading...")

        if invalidCaption: break
    if invalidCaption:
        print "Recreating invalid hit..."
        embedded_url = embedded_urls[HIT_IDs.index(invalidHit)]
        validHit = HITGeneration.GenerateCaptionHIT(mtc, 1, assignmentNum, [embedded_url]);
        HIT_IDs.pop(HIT_IDs.index(invalidHit))
        HIT_IDs.append(validHit)
        embedded_urls.pop(embedded_urls.index(embedded_url))
        embedded_urls.append(embedded_url)

    #rebuild arrays
    print "Count = " + str(count)
    print "---------------- NO MORE CAPTION HITS TO FIND -----------------------"
    print Completed_HITs
        
    #-------------------------------
    #--- Validation Holding Loop ---
    #-------------------------------
    #By this time all validation HITs have been generated (if any)
    wx.CallAfter(dlg.Update,0,"Validating and Generating .srt File")
    #RedoCationHITs = []
    while y > 0 and count == 0 and not invalidCaption:
        print "Validation Count = " + str(Validation_HIT_Count)
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
                    for value in question_form_answer.fields:
                        HIT_Answers.append(value)
                        print value

                #TODO: Modify HIT_Answers[0] based on the desgin implementation (int, str, etc... as well as indicies)... 
                #Do a search/replace to be sure
                #Check if the answer is the "None of the above" choice
                if HIT_Answers[0] == "None of the Above":
                    HITId = HITGeneration.GenerateCaptionHIT(mtc, 1, assignmentNum, embedded_urls)[0]
                    RedoCaptionHITs.append(HITId)
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
    print "...... Popped out of validation loop......."
    if invalidCaption: 
        NewCount = count - len(Accepted_Answers)
        CaptionAndValidationLoop(dlg, mtc, HIT_IDs, NewCount, assignmentNum, embedded_urls, Completed_HITs, Accepted_Answers)
    elif len(RedoCaptionHITs) > 0:
        CaptionAndValidationLoop(dlg,mtc, RedoCaptionHITs, len(RedoCaptionHITs), assignmentNum, embedded_urls, Completed_HITs, Accepted_Answers)
    else:
        wx.CallAfter(dlg.Destroy)
'''
