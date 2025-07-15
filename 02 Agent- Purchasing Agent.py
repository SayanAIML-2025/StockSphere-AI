import sys
import warnings
import json
import os

from crewai import LLM
from crewai import Agent, Crew, Process, Task, LLM
from dotenv import load_dotenv
from src.orchestration_agent.tools.csv_tool import CreatePurchaseOrderTool

load_dotenv()


class CrewInvAgent():
    def __init__(self):

        self.agent_name = "inventory_agent"
        self.inv_agent_config = {}
        self.inv_task_config = {}

        self.llm = LLM(
            model=os.getenv("CREW_MODEL")
            
        )  #api_version=os.getenv("AZURE_API_VERSION") api_version="2023-05-15"


    def setup_agent_task_config(self):
        # self.inv_agent_config, self.inv_task_config = self.get_config()

        Agent_=  Agent(
            role="Raw Materials Inventory Manager",
            goal="Monitor raw materials inventory levels and create purchase orders for materials that need restocking",
            backstory="You're a detail-oriented inventory manager responsible for ensuring client's raw materials are always  adequately stocked. You analyze demand forecasts, compare them with current inventory levels,  and proactively create purchase orders to prevent stockouts of essential raw materials.",
            tools=[CreatePurchaseOrderTool()],
            verbose= True, #self.inv_agent_config['verbose'],
            llm = self.llm,
            max_iter = 20, # Maximum iterations before the agent must provide its best answer.
            max_rpm = 10,  # Maximum requests per minute to avoid rate limits.
            max_retry_limit = 2, # Maximum number of retries when an error occurs.
            reasoning = False # Whether the agent should reflect and create a plan before executing a task.
            #max_reasoning_attempts = 2, # Maximum number of reasoning attempts before executing the task. If None, will try until ready.

        )

        desc= """
            Process the user query: "{user_query}" by analyzing the current inventory ("{current_inventory_file}") and demand forecast ("{forecast_file}") files, considering the conversation history ("{convo_summary}") for context. Provide inventory insights relative to demand, keep the user informed about product/raw material needs, and proactively create purchase orders if forecasted demand exceeds current inventory. Always recommend ordering based on forecasted and re-order levels; if inventory matches forecast exactly, consider an inventory buffer and advise ordering more if feasible. Never suggest or place orders below forecast/re-order levels, and if requested, respond politely with reasoning. If inventory is already sufficient, politely decline to create purchase orders, explaining the reasoning. For each required purchase order, return a properly formatted response including all fields defined in the tool.
        """     

# Analyze and inform if the forecasted quantity meets current inventory level and purchase order does not required to be created. Return a proper framed response of purchase order/s for raw materials where forecasted quantity exceeds current inventory.The purchase order response should include all the fields defined in the tool.

        expected_output= """
        A Response with purchase order details if created including all the necessary details fields from the fianl purchase order summary. Include a summary report with analytical and business related insights of the purchase order details in comparision with its inventory and forecast data.
        """

#Create a purchase order CSV file at "{purchase_order_file}" for raw materials where forecasted quantity exceeds current inventory. The purchase order should include Purchase_Order_ID, RawMaterial_ID, RawMaterial_Name, and RawMaterial_Quantity (difference between forecast required and current).


        Task_= Task (
            description=desc, #self.inv_task_config['task_desc'],  
            expected_output=expected_output,  #self.inv_task_config['task_output'],
            tools=[CreatePurchaseOrderTool()],
            agent= Agent_
        )   # output_file=self.inv_task_config['output_file']   #ReadCSVTool(),

        return Agent_, Task_


    def task_execution(self, context):
        print("Entering task inventory")
        agent_, task_ = self.setup_agent_task_config()

        res = agent_.execute_task(task=task_,
        context=context)

        return res