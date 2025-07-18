#!/usr/bin/env python
import shutil
# from random import randint
# from tempfile import tempdir
from pydantic import BaseModel

from crewai.flow import Flow, listen, start
from src.utils.intent import Intent

from src.orchestration_agent.crews.orchestrator_flow.Purchasing_Agent import CrewInvAgent
from src.orchestration_agent.crews.orchestrator_flow.Supplier_Selection_Agent import CrewSrcAgent
from src.orchestration_agent.crews.orchestrator_flow.Inventory_Analyst import CrewQryAgent


class OrchState(BaseModel):
    intent: str = ""
    convo: list = []
    convo_summary: str = ""
    user_query: str = ""
    files_dict: dict = {}
    tmp_dir: str = ""


class OrchestrationFlow(Flow[OrchState]):

    assistant_res:str = ""

    @start()
    def intent_classification(self):
        try:
            print("Generating intent - triggering process")

            self.state.files_dict = {'forecast_file':'demand_forecast.csv','current_inventory_file':'inventory.csv'}  # Copy the relative paths here for both the files.....this is accessible only for crew flow

            intentclass_object = Intent()

            if len(self.state.convo) > 1:
                intent, convo_summary, user_query = intentclass_object.identify_intent(self.state.convo)
                self.state.convo_summary = convo_summary
                self.state.intent = intent.strip()
                self.state.user_query = user_query
                
            else:
                intent, user_query = intentclass_object.identify_intent(self.state.convo)
                self.state.intent = intent.strip()
                self.state.user_query = user_query
        
            print("In main.py - Identified Intent:", self.state.intent)

            # blob_files, temp_dir = file_load_from_blob()   #file_load_from_db()     
            # self.state.files_dict = blob_files
            # self.state.tmp_dir = temp_dir

        except Exception as e:
            print("Error in generating Intent:",e)

    @listen(intent_classification)
    def inventory_agent(self):
        
        if self.state.intent == "PO creation intent":
            try:  
                # self.state.files_dict = blob_files
                # self.state.tmp_dir = temp_dir
                print("Triggering Inventory Agent, PO creation intent identified")

                context ={
                    'forecast_file': self.state.files_dict['forecast_file'],
                    'current_inventory_file': self.state.files_dict['current_inventory_file'],
                    'user_query': self.state.user_query,
                    'convo_summary': self.state.convo_summary
                }   # 'purchase_order_file': self.state.files_dict['purchase_order_file'],

                result = CrewInvAgent().task_execution(context)

                print("Result:",result)

                self.assistant_res = result

            except Exception as e:
                print("Error while triggering Inventory agent:",e )

    @listen(intent_classification)
    def query_assistant(self):
        if self.state.intent == "Inventory query intent":
            try:
                print("Triggering Query Assistant Agent, Inventory query intent identified")

                context ={
                    'user_query': self.state.user_query,
                    'convo_summary': self.state.convo_summary
                }
                result = CrewQryAgent().task_execution(context)

                print("Result:",result)

                self.assistant_res = result

            except Exception as e:
                print("Error while triggering Query Assistant agent:",e)

    
    @listen(intent_classification)
    def sourcing_manager(self):
        if self.state.intent == "Supplier recommendation intent":
            try:
                print("Triggering Sourcing Agent, Supplier recommendation intent identified")

                context ={
                    'user_query': self.state.user_query,
                    'convo_summary': self.state.convo_summary
                }

                result = CrewSrcAgent().task_execution(context)

                print("Result:",result)
                
                self.assistant_res = result

            except Exception as e:
                print("Error while triggering Query Assistant agent:",e)


    @listen(intent_classification)
    def other_intent(self):
        if self.state.intent == "Other":
            try:
                print("Intent Identifid as 'Other'")
                
                self.assistant_res = "I am not able to map your query to any intent, kindly redefine your your query"

            except Exception as e:
                print("Error while triggering Query Assistant agent:",e)
            

def kickoff(convo):
    state=OrchState(convo = convo)
    orch_flow = OrchestrationFlow(state=state)
    orch_flow.kickoff(inputs={"convo": convo})
    assistant_res_ = orch_flow.assistant_res
    print("System Output:",assistant_res_)

    return assistant_res_


# def plot():
#     poem_flow = PoemFlow()
#     poem_flow.plot()


# if __name__ == "__main__":
#     convo =[
#         {
#             "role": "user",
#             "content": "Hello"
#         },
#         {
#             "role": "system",
#             "content": "Hello! How can I assist you today?"
#         },
#         {
#             "role": "user",
#             "content": "create a purchase order for RM002"
#         }
#     ]

#     from utils.agents_api import external_apis
#     import asyncio
#     checks, api_results = asyncio.run(external_apis(ques_input=convo[-1]['content']))

#     kickoff(convo,api_results)
