#!/usr/bin/env python

from src.utils.functions import is_greeting, greeting_response
# from utils.data_models import MainAgentSchema
from src.main import kickoff
from pydantic import BaseModel


class MainAgentSchema(BaseModel):
    """
    Schema for app.py input message
    """
    messages: list

def run_stocksphere(payload: MainAgentSchema):
    
    # payload = payload.dict()
    # payload = payload.model_dump()

    convo = payload["messages"]
    print(convo)
    # convo = payload

    if convo[-1] and convo[-1]['role']=='user':
        try:
            
            # checks, api_results = run_asyncio(ques_input=convo[-1]['content'])   

            welcome_intent = is_greeting(convo[-1]['content'])
            welcome_response = greeting_response()
            print(welcome_intent)
            print(welcome_response)
            
            if welcome_intent == True:
                assistant_message = {"role": "system", "content": welcome_response}
                convo.append(assistant_message)
                return {
                    "messages": convo
                }

            else:
                
                try:
                    print("Kickoff Flow command triggered")
                    try:
                        result = kickoff(convo)
                        print("App:",result)
                        assistant_message = {"role": "system", "content": result}
                        convo.append(assistant_message)

                        # Return the serialized response
                        return {
                            "messages": convo
                        }

                    except Exception as e:
                        print("ERROR while executing Kickoff !")

                
                # except HTTPException as e:
                except Exception as e:
                    print("Error in Kickoff call:",e)
                    assistant_message = {"role": "system", "content": f'Error: Please try again, details: {str(e)}'}
                    convo.append(assistant_message)
                    # return convo
                    return {
                        "messages": convo
                    }

        except Exception as e:
            print("Error in Payload access or Payload processing:",e)
            assistant_message = {"role": "system", "content": f'Error: Please try again, details: {str(e)}'}
            convo.append(assistant_message)
            # return convo
            return {
                    "messages": convo
                }
    else:
        print("User input missing")
        assistant_message = {"role": "system", "content": 'Error: Please try again, details: User Input missing'}
        convo.append(assistant_message)
        # return convo
        return {
                "messages": convo
            }


# if __name__ == "__main__":
#     conversation={'messages': [{'role': 'user', 'content': 'do we have enough salt?'}]}
#     #, {'role': 'system', 'content': 'Greetings from Stocksphere AI. How may I help you with your supplier or inventory management needs?'}, {'role': 'user', 'content': 'Help me create a purchase order for Salt'}, {'role': 'system', 'content': 'Based on the analysis of current inventory levels and demand forecast data, the inventory for Salt is already sufficient to meet the forecasted needs. Therefore, no purchase order has been created. Restocking is not required at this time, and current inventory levels are adequate to fulfill forecasted demand. If additional assistance is needed or further analysis is required, feel free to ask!'},{'role': 'user', 'content': 'Help me create a purchase order for Sugar'}]}   
#     result = run_stocksphere(conversation)
#     print('stocksphere resp',result)
    

