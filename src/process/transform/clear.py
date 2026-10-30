from src.process.transform.nlp import nlp
from src.process.df_columns import dfColumns

def compact_text(data):
  new_contents = nlp.pipe(data[dfColumns.content.value], batch_size=50)
  compact_new_content = []
  new_ents = []
  for new in new_contents:
    new_ents.append([(ne.text, ne.label_) for ne in new.ents])
    compact_new = ""
    left = 0
    for i, en in enumerate(new.ents):
      left = new.ents[i-1].end if i > 0 else 0
      compact_new += new[left:en.start].text_with_ws + en.text.replace(" ", "_") + " "
      left = new.ents[i].end
      
    if left < len(new):
      compact_new += str(new[left:])
    compact_new_content.append(compact_new)
  
  new_contents = [" ".join([token.text if '_' in token.text else token.lemma_ for token in doc if not token.is_stop and not token.is_punct]) 
                    for doc in nlp.pipe(compact_new_content, batch_size=50)]
  
  return new_contents, new_ents
  
def clear(data):
  data[dfColumns.content.value], data[dfColumns.ne.value] = compact_text(data)
  print(data[dfColumns.content.value][0])
  print(data[dfColumns.ne.value][0])
  return data