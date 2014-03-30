'''
Texas A&M University - Spring 2014 - CSCE 438
HW3 - CrowdCaptioners

CrowdCaptioners Team:
Vishal Anand
Travis Purcell
Ricardo Zavala

File Created by: Travis Purcell, Ricardo Zavala

Purpose:  Contains functions to create HITs
'''
#-------------------------------
# ----------- Import -----------
#-------------------------------
from boto.mturk.question import QuestionContent,Question,QuestionForm,Overview,AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer
import os
#-------------------------------
#-------- Config Globals -------
#-------------------------------

#Total Price  = ((Caption_Price * assignmentNum) + Validation_Price)(video segments) + Tax
#Choose Wisely...
Caption_Price = 0.01
Validation_Price = 0.01

#-------------------------------
# --------- Functions ----------
#-------------------------------

# Helper function to save the generated HIT and assignments
# Although it is fully functional, it is not being really used for anything critical
def save_file(hit_type_ids, title, n, hit_ids):
    if hit_type_ids.count(hit_type_ids[0]) == n:
        print "Creating save file.  File saved will be saved as:"
        file_name = "%s.sav" % title
        print file_name
        if os.path.exists(file_name):
            print "Collision detected.  Deleting previous save file..."
            os.remove(file_name)
        with open(file_name, 'w') as myFile:
            myFile.write(hit_type_ids[0] + "\n")
            for r in range(0, len(hit_ids)):
                myFile.write(hit_ids[r] + "\n")
        return True
    return False

#Generates N HITs, Returns a list of HIT IDs
def GenerateCaptionHIT(mtc, n, assignmentNum, embedded_urls, data_title):
    HIT_IDs = []
    HIT_Type_IDs = []
    for i in range(0, n):
        title = 'Transcribe a short video segment'
        description = 'Watch a short segment of a video and enter a transcription of it'
        keywords = 'video, captioning, short'
        ratings = [('Long (&gt;1 min)', '-2'),
                   ('Medium (&gt;15 secs, &lt;1 min)', '-1'),
                   ('Short (&lt;15 secs)', '1')]

        #---------------  BUILD OVERVIEW -------------------
        overview = Overview()
        overview.append_field('Title', title)
        overview.append(FormattedContent('<h3><span style="font-family:verdana,geneva,sans-serif;">CrowdCaptioners - Transcribing done a short segment at a time</span></h3>'
                                         '<div class="highlight-box"><p><span style="font-family:verdana,geneva,sans-serif;">For this task, you are asked to transcribe a short segment of a video. &nbsp;Your goal is to provide as accurate a transcription as possible <strong>without worrying too much about punctuation</strong>. &nbsp;The steps to take (to minimize the time you need to spend working on this task) should be the following:</span></p>'
                                         '<ul><li><span style="font-family:verdana,geneva,sans-serif;">Open up a note taking program (notepad, textedit, etc.)</span></li><li><span style="font-family:verdana,geneva,sans-serif;">Click on the link below, which will send you over to a short video segment.</span></li><li><span style="font-family:verdana,geneva,sans-serif;">Carefully listen to the video and type down on your note taking program the dialog spoken on the video (again, you do not need to worry about punctuation, <u>unless it is really obvious</u>.)</span></li><li><span style="font-family:verdana,geneva,sans-serif;">Once you have transcribed the whole short little video segment, come back to this page. You should be able to answer the short question below.</span></li><li><span style="font-family:verdana,geneva,sans-serif;">Finally, copy the contents of your note taking application and paste them into the text box area at the end of the task and&nbsp;<span style="line-height: 1.6em;">submit your answers!</span></span></li></ul></div>'
                                         '<h4><span style="font-family:verdana,geneva,sans-serif;"><a href="' + embedded_urls[i] + '" target="_blank">Click here to watch the video segment to transcribe</a></span></h4>'
                                         ))

        #---------------  BUILD QUESTION 1 -------------------
        qc1 = QuestionContent()
        qc1.append_field('Title', '1. How long was the video segment?:')

        fta1 = SelectionAnswer(style='radiobutton', selections=ratings)
        q1 = Question(identifier='design', content=qc1,
                      answer_spec=AnswerSpecification(fta1),
                      is_required=True)

        #---------------  BUILD QUESTION 2 -------------------
        qc2 = QuestionContent()
        qc2.append_field('Title', '2. Provide your transcription of the video:')

        fta2 = FreeTextAnswer()

        q2 = Question(identifier='comments', content=qc2,
                      answer_spec=AnswerSpecification(fta2))

        #--------------- BUILD THE QUESTION FORM -------------------
        question_form = QuestionForm()
        question_form.append(overview)
        question_form.append(q1)
        question_form.append(q2)

        #--------------- CREATE THE HIT -------------------
        new_hit = mtc.create_hit(questions=question_form,
                                 max_assignments=assignmentNum,
                                 title=title,
                                 description=description,
                                 keywords=keywords,
                                 duration=60 * 3,
                                 reward=Caption_Price)
        print new_hit[0].HITId
        HIT_Type_IDs.append(new_hit[0].HITTypeId)
        HIT_IDs.append(new_hit[0].HITId)
        i += 1
        #End of loop

    #Save the generated HIT so it can be loaded later
    if not save_file(HIT_Type_IDs, data_title, n, HIT_IDs):
        print "HITs were created in different groups...\nNo save file can be created."

    print "https://workersandbox.mturk.com/mturk/preview?groupId="+new_hit[0].HITTypeId

    return HIT_IDs

###-- NOT EDITED YET --###
#Generates a validation HIT, Takes a Caption HIT ID, a list of possible answers and returns a validation HIT ID
def GenerateValidationHIT(mtc, PossibleAnswers, embedded_url):
    title = 'Check the following options for the correct caption'
    description = ('Select the caption that better transcribes what is'
                    ' said in a video')
    keywords = 'video, rating, validation'

    ratings = [('No','0'),
               ('Yes','1')]
    CorrectAnswer = [(PossibleAnswers[0],'0'),
                     (PossibleAnswers[1],'1'),
                     ('None of the above','2')]

    #--------------- BUILD OVERVIEW -------------------

    overview = Overview()
    overview.append_field('Title', title)
    overview.append(FormattedContent('<a target="_blank"'
                                     ' href="' + embedded_url + '">'
                                     ' Click here for the short video</a>'))

    #--------------- BUILD QUESTION 1 -------------------

    qc1 = QuestionContent()
    qc1.append_field('Title','Where you required to leave this page to complete the HIT?')

    fta1 = SelectionAnswer(min=1, max=1,style='dropdown',
                            selections=ratings,
                            type='text',
                            other=False)

    q1 = Question(identifier='design',
                    content=qc1,
                    answer_spec=AnswerSpecification(fta1),
                    is_required=True)

    #--------------- BUILD QUESTION 2 -------------------

    qc2 = QuestionContent()
    qc2.append_field('Title','What is the correct transcription?')

    fta2 = SelectionAnswer(min=1, max=1,style='radiobutton', selections=CorrectAnswer, type='text', other=False)#fta2 = FreeTextAnswer()

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
                    duration = 60 * 3,
                    reward = Validation_Price)


    print new_hit[0].HITId
    #print new_hit[0].HITTypeId
    print "\nValidation hit group = : https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit[0].HITTypeId +"\n"

    return new_hit[0].HITId

'''
Reference:
HIT Data Structure (returned by create_hit)

<HIT>
  <HITId>123RVWYBAZW00EXAMPLE</HITId>          - ID of Hit
  <HITTypeId>T100CN9P324W00EXAMPLE</HITTypeId> - The Website Link ID
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
'''
