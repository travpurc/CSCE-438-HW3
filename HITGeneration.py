'''
Texas A&M University - Spring 2014 - CSCE 438
HW3 - CrowdCaptioners

CrowdCaptioners Team:
Vishal Anand
Travis Purcell
Ricardo Zavala

File Created by: Travis Purcell, Ricardo Zavala

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

#-------------------------------
# ----------- Import -----------
#-------------------------------

from boto.mturk.question import QuestionContent,Question,HTMLQuestion,QuestionForm,Overview,AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer

#-------------------------------
#-------- Config Globals -------
#-------------------------------

#Total Price  = ((Caption_Price * assignmentNum) + Validtion_Price)(video segments) + Tax
#Choose Wisely...
Caption_Price = 0.01
Validtion_Price = 0.01

#-------------------------------
# --------- Functions ----------
#-------------------------------

#Generates N HITs, Returns a list of HIT IDs
def GenerateCaptionHIT(mtc, n, assignmentNum, embedded_urls):
    HIT_IDs = []
    for i in range(0, n):
        title = 'Provide a caption of a following video'
        description = ('Watch a short video and type in a transcription'
                       ' of it')
        keywords = 'video, captioning, short'
        ratings =[('Short (&lt;15 secs)','-1'),
                 ('Medium (&gt;15 secs, &lt;1 min)','0'),
                 ('Long (&gt;1 min)','1')]
 
        #---------------  BUILD OVERVIEW -------------------
 
        overview = Overview()
        overview.append_field('Title', title)
        overview.append(FormattedContent('<a target="_blank"'
                                         ' href="' + embedded_urls[i] + '">'
                                         ' Click here for the short video</a>'
                                         ))
 
        #---------------  BUILD QUESTION 1 -------------------
 
        qc1 = QuestionContent()
        qc1.append_field('Title','Is the video:')
 
        fta1 = SelectionAnswer(min=1, max=1,style='dropdown',
                              selections=ratings,
                              type='text',
                              other=False)
        #q1 = HTMLQuestion('<iframe id="ytplayer" type="text/html" width="640" height="360" src="'+embedded_urls[i]+'" frameborder="0" allowfullscreen>', 700)
        q1 = Question(identifier='design',
                      content=qc1,
                      answer_spec=AnswerSpecification(fta1),
                      is_required=True)
 
        #---------------  BUILD QUESTION 2 -------------------
 
        qc2 = QuestionContent()
        qc2.append_field('Title','What are the words spoken in the video?')
 
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
 
        #Pretty sure we are going to have to link out to a video...
        #hitContent = '<!DOCTYPE html> <html lang=en><head><meta charset=utf-8><title>Hello World</title></head><body><h1>VIdeo</h1><p>Just testing....</p></body></html>'
        #html_question = HTMLQuestion(hitContent, 500)

        new_hit = mtc.create_hit(questions=question_form,
                       max_assignments=assignmentNum,
                       title=title,
                       description=description,
                       keywords=keywords,
                       duration = 60*2,
                       reward = Caption_Price)
    
    
        print new_hit[0].HITId
        #print new_hit[0].HITTypeId
        print "https://workersandbox.mturk.com/mturk/preview?groupId="+new_hit[0].HITTypeId

        HIT_IDs.append(new_hit[0].HITId)
        i+=1
        #End of loop
    return HIT_IDs

#Generates a validation HIT, Takes a Caption HIT ID, a list of possible answers and returns a validation HIT ID
def GenerateValidationHIT(mtc, PossibleAnswers, embedded_url):
    title = 'Check the following options for the correct caption'
    description = ('Select the caption that better transcribes what is'
                    ' said in a video')
    keywords = 'video, rating, validation'
 
    ratings = [('No','0'),
               ('Yes','1')]#,
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
                    duration = 60 * 2,
                    reward = Validtion_Price)
    
    
    print new_hit[0].HITId
    #print new_hit[0].HITTypeId
    print "https://workersandbox.mturk.com/mturk/preview?groupId=" + new_hit[0].HITTypeId

    return new_hit[0].HITId

