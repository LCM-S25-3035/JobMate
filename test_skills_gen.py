from app.question.question_gen import generate_questions_from_skills
qs = generate_questions_from_skills('Python, SQL', 'expert', 'technical', 'English', 10)
print('Generated', len(qs))
for i,q in enumerate(qs,1):
  print(i, q['text'][:70].replace('\n',' ') )
