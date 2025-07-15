import os
from dotenv import load_dotenv
from src.utils.constants import INTENT_PROMPT
from src.utils.functions import llm_completions
import google.generativeai as genai
 
load_dotenv()


class Intent():

    def __init__(self) -> None:
        pass
 
    
    def summarize_conversation(self,conversation_history):
        """
        Summarizes the entire conversation history using the LLM.
        """
        try:
            print("Processing past conversations")
            convo_text = ""
            for turn in conversation_history:
                convo_text += f"{turn['role'].capitalize()}: {turn['content']}\n"
    
            summary_prompt = f"""
            Summarize the following conversation in a concise paragraph, making sure to retain the context of the conversation:
            {convo_text}
            Summary:
            """

            message = [{"role": "user", "content": summary_prompt}]
    
            summary = llm_completions(message)

            # logger.info(f"Summary generated: {summary}")
            print("Summary generated:",summary[0:40],".............",summary[len(summary)-100:])
            return summary
    
        except Exception as e:
            print("Error summarizing past conversations:",e)
    
    def check_intent_with_llm(self, query, LastTwoConvo):
        """
        Checks the intent of a query using an LLM and returns the predicted intent.
        """
        try:

            prompt = INTENT_PROMPT + f"query: {query}, Conversation History Summary: {LastTwoConvo}"

            # message=[
            #         {"role": "system", "content": "You are a helpful assistant that only returns one of the four intent categories, without any explanation."},
            #         {"role": "user", "content": prompt}
            #     ]

            message=[
                    {"role": "user", "content": prompt}
                ]
            # print('input message for intent classification',message[-1]['content'])
            intent = llm_completions(message)

            print("Checking Intent")
            print("Query:",query,"\nPredicted Intent:",intent)

            return intent
    
        except Exception as e:
            print("Error during intent classification:",e)


    def identify_intent(self,conversation_history ) -> str:   
        # Example payload -->
        # {

        # messages: 
        # [

        # {"role": "user", "content": "Hi"},
        # {"role": "system", "content": "Hello, How can I help you!"},
        # {"role": "user", "content": "What should I do handle deficient materials?"},   # returns intent
        # {"role": "system", "content": "Response"},
        # {"role": "user", "content": "nextquery"},

        # ]
        # }
        # }
        try:
            summarized_history=""
            user_query = conversation_history[-1]['content']  # Assuming we are getting user query integrated with proper dict structure in the convo_hist from UI

            print("Processing user's query:",user_query)

            LastTwoConvo = conversation_history[-3:]

            # print('LastTwoConvo',LastTwoConvo)
            # print("LastTwoConvo:",str(LastTwoConvo)[0:40],".............",str(LastTwoConvo)[len(str(LastTwoConvo))-100:])

            intent = self.check_intent_with_llm(user_query, LastTwoConvo)

            if len(conversation_history) > 1:
                summarized_history = self.summarize_conversation(conversation_history[:-1])


            if summarized_history != "":
                return intent, summarized_history, user_query
            else:
                print("Intent Identified:",intent)
                return intent, user_query

        except Exception as e:
            print("Error in processing intent:",e)
            return {"response": 'Error: Please try again for intent generation',"messages":str(e)}


