import sys
import warnings
import json
import os
from crewai import LLM
from crewai import Agent, Crew, Process, Task, LLM

from dotenv import load_dotenv
from src.orchestration_agent.tools.query_tools import POCreationTool

load_dotenv()

class CrewQryAgent():
    def __init__(self):

        self.agent_name = "query_assistant"

        self.llm = LLM(
            model=os.getenv("CREW_MODEL")
        )

    def setup_agent_task_config(self):


        Agent_=  Agent(
            role="Inventory Data Analyst",
            goal="Analyze inventory and forecast data to provide factual answers about raw materials status",
            backstory="You're a data analyst specializing in inventory management. Your job is to analyze the raw materials inventory data and forecast data, and provide factual information  about the status of materials. You focus on identifying surpluses, shortages, and exact matches between current inventory and forecasted requirements.",
            tools=[QueryInventoryTool()],
            verbose=False, #self.qry_agent_config['verbose'],
            llm = self.llm,
            max_iter = 20, # Maximum iterations before the agent must provide its best answer.
            max_rpm = 10,  # Maximum requests per minute to avoid rate limits.
            max_retry_limit = 2, # Maximum number of retries when an error occurs.
            reasoning = False, # Whether the agent should reflect and create a plan before executing a task.max_reasoning_attempts = 2, # Maximum number of reasoning attempts before executing the task. If None, will try until ready.
        )


        desc="""
            Process user query: "{user_query}" through knowledge graph tool using the demand forecast data and compare it with the current inventory data. Analyze inventory and forecast data to provide factual answers about raw materials status. Identify raw materials where forecasted quantity exceeds current inventory. Analyze if the forecasted quantity meets current inventory level and assist the user whether to create a purchase order for that material or not. Consider the conversation history "{convo_summary}" with the user for context.

        """
        Task_= Task (
            description=desc, 
            expected_output="A detailed analysis of raw materials inventory shortages with material details and quantities needed.",
            tools=[QueryInventoryTool()],
            agent= Agent_
        )

        return Agent_, Task_



    def task_execution(self,context):
        
        agent_, task_ = self.setup_agent_task_config()
        print("Inside class running Task")
        res = agent_.execute_task(task=task_,
        context=context)

        return res
