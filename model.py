from groq import Groq
from config import api_key
from prompts import classifier, matcher
import json

class Model:
    def __init__(self):
        self.user=Groq(api_key=api_key)

    def classify(self,message):
        prompt=classifier
        output=self.user.chat.completions.create(model="openai/gpt-oss-20b", messages=[{
            "role":"system", "content":prompt},
            {"role":"user", "content":message}],
            temperature=0.1,
            max_tokens=1500 )
        return json.loads(output.choices[0].message.content)

    def task_matcher(self,tasks, classifer_intent):
        prompt=matcher
        user_content=f"task:{classifer_intent}, task_list:{tasks}"
        output=self.user.chat.completions.create(model="openai/gpt-oss-20b", messages=[{
                    "role":"system", "content":prompt},
                    {"role":"user", "content":user_content}],
                    temperature=0.1,
                    max_tokens=1500 )
        return json.loads(output.choices[0].message.content)
