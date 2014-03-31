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

def make_direct_validation_hit(hit_id, completed_hits, urls):
    #TODO
    #read hit id, find its position in completed_hits (/2)
    #and extract that url to generate NEW (not validation) hit
    #update completed hit with new hitID
    pass

def find_position(hit_id, completed_hits):
    index = 0
    was_found = False
    can_continue = True
    print "Entering Find Loop"
    while not was_found:
        print "Inside Find Loop: %i" % index
        if not can_continue:
            break
        current_id = completed_hits[index][0]
        print "Current ID:"
        print current_id
        if hit_id == "":
            print "hit_id == '' "
            #was_found = True
            break
        if hit_id == current_id:
            print "position in Completed_Hits found: %i" % index
            was_found = True
            break
        index += 1
        if index == len(completed_hits):
            can_continue = False
    if was_found:
        print "was found!"
        return index
    print "\n---Shouldn't be here!!---\n"
    return -1

#Evaluates similarity of two strings and returns a bool
def similar(string1, string2, hurdle):
    return difflib.SequenceMatcher(a=string1.lower(), b=string2.lower()).ratio() > hurdle

def make_validation_hit(mtc, options, url):
    return HITGeneration.GenerateValidationHIT(mtc, options, url)

# answers is a list of lists of lists of (HIT_ID, answer).
# It contains all "answers" from a single HIT in a list of lists of (HIT_ID, answer)
def validate(hit_answers, completed_hits, mtc, hit_ids, urls):
    valid_answers = []
    for hit_group in hit_answers:
        assignment1 = 0
        assignment2 = 1
        # HIT_ID for assignment1
        id_r = hit_group[assignment1][0]
        print "id_r:"
        print id_r
        # TODO: SHOULD NOT GET HERE!
        if id_r == "":
            continue
        print "Length of HIT group:"
        print len(hit_group)
        if len(hit_group) > 2:                  # There are more than 2 assignments... Compare 1 and 3
            assignment2 = len(hit_group)/2
        print "assignment2:"
        print assignment2
        # HIT_ID for assignment2
        id_s = hit_group[assignment2][0]
        print "id_s:"
        print id_s
        '''
        if len(hit_group) > 2: # There were repeats... Compare 1 and 3
            assignment2 -= 1
        print "assignment2-1:"
        print assignment2
        print "new assignment[assignment2][0]:"
        print hit_group[assignment2][0]

        answer1 = hit_group[assignment1][1]
        answer2 = hit_group[assignment2][1]
        '''
        caption1 = hit_group[assignment1][1]
        caption2 = hit_group[assignment2][1]
        index_caption1 = find_position(id_r, completed_hits)
        index_caption2 = index_caption1 + 1
        # This should not happen, except after an invalid security answer:
        if id_r != id_s:
            index_caption2 = find_position(id_s, completed_hits)
            #print u/2
        print index_caption1
        print index_caption2
        if similar(caption1, caption2, validationHurdle):
            print index_caption2
            print index_caption2/2
            valid_answers.append([index_caption2/2, caption1])
        else:
            make_validation_hit(mtc, [caption1, caption2], urls[hit_ids.index(id_r)])
    return valid_answers

def check_results(mtc, completed_hits, hit_ids, urls):
    answers = []
    hits_available = get_all_reviewable_hits(mtc)
    for hit in hits_available:
        hit_id = hit.HITId
        mtc.set_reviewing(hit_id)
        assignments = mtc.get_assignments(hit_id)
        temp = []
        for assignment in assignments:
            for question_form_answer in assignment.answers[0]:
                r = 0
                for answer in question_form_answer.fields:
                    print answer
                    # Answer to the security question:
                    if r == 0:
                        # If answer != 1, generate new hit, append the new HIT_ID to the answers to validate...
                        if answer != '1':
                            hit_id = make_direct_validation_hit(hit_id, completed_hits, urls)
                            temp.append([hit_id, ""])
                            # ... and skip the next answer (caption)
                            r += 2
                            continue
                        r += 1
                    # Caption!
                    elif r == 1:
                        temp.append([hit_id, answer])
                # End first for
            # End second for
        answers.append(temp)
    answers = validate(answers, completed_hits, mtc, hit_ids, urls)
    return answers

#By FAR the most time consuming function
#Returns a list of validated answers
def CaptionAndValidationLoop(dlg, mtc, HIT_IDs, count, assignmentNum, embedded_urls, Completed_HITs, Accepted_Answers):
    # The completion percentage can be obtained by remaining_hits/total_hits*100
    total_hits = count*assignmentNum
    remaining_hits = total_hits
    while remaining_hits > 0:
        captions = check_results(mtc, Completed_HITs, HIT_IDs, embedded_urls)
        valid_answers = merge_answers(captions, Accepted_Answers)
        print valid_answers
        if valid_answers > 0:
            remaining_hits -= valid_answers
        else:
            print Accepted_Answers
            time.sleep(30)

'''
def check_results(mtc, completed_hits, hit_ids, urls):
    answers = []
    hits_available = get_all_reviewable_hits(mtc)
    for hit in hits_available:
        hit_id = hit.HITId
        mtc.set_reviewing(hit_id)
        assignments = mtc.get_assignments(hit_id)
        for assignment in assignments:
            temp = []
            for answer in assignment.answers[0]:
                r = 0
                for value in answer.fields:
                    print value
                    if r == 0:
                        if value != '1':
                            hit_id = make_direct_validation_hit(hit_id, completed_hits, urls)
                            temp.append(hit_id)
                            temp.append("")
                            r += 1
                        r += 1
                    elif r == 1:
                        temp.append(hit_id)
                        temp.append(value)
                        r += 1
                # End first for
            answers.append(temp)
            # End second for
    answers = validate(answers, completed_hits, mtc, hit_ids, urls)
    return answers
'''
