

# Import
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import QuestionContent,Question,QuestionForm,Overview,AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer

ACCESS_ID ='AKIAIMZSF4GBOL4QTGTA'
SECRET_KEY = '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'
HOST = 'mechanicalturk.sandbox.amazonaws.com'

mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                      aws_secret_access_key=SECRET_KEY,
                      host=HOST)

print mtc.get_account_balance() 


title = 'Give your opinion about a website'
description = ('Visit a website and give us your opinion about'
               ' the design and also some personal comments')
keywords = 'website, rating, opinions'
 
ratings =[('Very Bad','-2'),
         ('Bad','-1'),
         ('Not bad','0'),
         ('Good','1'),
         ('Very Good','1')]
 
#---------------  BUILD OVERVIEW -------------------
 
overview = Overview()
overview.append_field('Title', 'Give your opinion on this website')
overview.append(FormattedContent('<a target="_blank"'
                                 ' href="http://www.toforge.com">'
                                 ' Mauro Rocco Personal Forge</a>'))
 
#---------------  BUILD QUESTION 1 -------------------
 
qc1 = QuestionContent()
qc1.append_field('Title','How looks the design ?')
 
fta1 = SelectionAnswer(min=1, max=1,style='dropdown',
                      selections=ratings,
                      type='text',
                      other=False)
 
q1 = Question(identifier='design',
              content=qc1,
              answer_spec=AnswerSpecification(fta1),
              is_required=True)
 
#---------------  BUILD QUESTION 2 -------------------
 
qc2 = QuestionContent()
qc2.append_field('Title','Your personal comments')
 
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
 
new_hit = mtc.create_hit(questions=question_form,
               max_assignments=1,
               title=title,
               description=description,
               keywords=keywords,
               duration = 60*5,
               reward=0.05)


'''
HIT Data Structure

<HIT>
  <HITId>123RVWYBAZW00EXAMPLE</HITId>
  <HITTypeId>T100CN9P324W00EXAMPLE</HITTypeId> - The Website ID
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

print new_hit[0].HITId
print new_hit[0].HITTypeId

#def get_all_reviewable_hits(mtc):
#    page_size = 50
#    hits = mtc.get_reviewable_hits(page_size=page_size)
#    print "Total results to fetch %s " % hits.TotalNumResults
#    print "Request hits page %i" % 1
#    total_pages = float(hits.TotalNumResults)/page_size
#    int_total= int(total_pages)
#    if(total_pages-int_total>0):
#        total_pages = int_total+1
#    else:
#        total_pages = int_total
#    pn = 1
#    while pn < total_pages:
#        pn = pn + 1
#        print "Request hits page %i" % pn
#        temp_hits = mtc.get_reviewable_hits(page_size=page_size,page_number=pn)
#        hits.extend(temp_hits)
#    return hits

#hits = get_all_reviewable_hits(mtc)
 
#for hit in hits:
#    assignments = mtc.get_assignments(hit.HITId)
#    for assignment in assignments:
#        print "Answers of the worker %s" % assignment.WorkerId
#        for question_form_answer in assignment.answers[0]:
#            for key, value in question_form_answer.fields:
#                print "%s: %s" % (key,value)
#        print "--------------------"