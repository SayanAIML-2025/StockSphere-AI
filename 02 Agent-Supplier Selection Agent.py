import sys
import warnings
import json
import os
from crewai import LLM
from crewai import Agent, Crew, Process, Task, LLM

from dotenv import load_dotenv
from src.orchestration_agent.tools.supplier_tools import SupplierRecommendationTool

load_dotenv()

class CrewSrcAgent():
    def __init__(self):

        self.agent_name = "sourcing_agent"

        self.llm = LLM(
            model=os.getenv("CREW_MODEL"),
        )


    def setup_agent_task_config(self):

        Agent_=  Agent(
            role="Raw Materials Sourcing Manager",
            goal="Analyze supplier evaluations and select the optimal suppliers for the raw materials procurement needs.",
            backstory="You're a senior strategic sourcing professional with extensive experience in supplier selection and management for raw materials. You're skilled at evaluating suppliers based on multiple criteria including price, delivery time, historical performance, and quality ratings to make data-driven decisions that balance cost, quality, and reliability.",
            tools=[SupplierRecommendationTool()],
            verbose=False, #self.src_agent_config['verbose'],
            llm = self.llm,
            max_iter = 20, # Maximum iterations before the agent must provide its best answer.
            max_rpm = 10,  # Maximum requests per minute to avoid rate limits.
            max_retry_limit = 2, # Maximum number of retries when an error occurs.
            reasoning = False, # Whether the agent should reflect and create a plan before executing a task.max_reasoning_attempts = 2, # Maximum number of reasoning attempts before executing the task. If None, will try until ready.
        )

        desc= """
            Process user query: "{user_query}" through knowledge graph tool. Analyze suppliers recommendation and provide a summary report with insights on the recommendation response. Consider the conversation history "{convo_summary}" with the user for context. Tool execution involves knowledge graph API hit,your responsibility is to display that input appropriately. If the Dynamic KG API does not returns the ouptut in one go or returns empty results '[]',convey the same in the response politely to the user with proper reasoning. 

        """   #retry hitting the API again. Max you can try 2 times to trigger the API execution.
        Task_= Task (
            description=desc,
            expected_output="A comprehensive supplier evaluation with scores, rankings, and selected suppliers for each raw material. Include a detailed explanation of the evaluation methodology and final recommendations.",
            tools=[SupplierRecommendationTool()],
            agent= Agent_
        )
        return Agent_, Task_



    def task_execution(self,context):
        agent_, task_ = self.setup_agent_task_config()

        res = agent_.execute_task(task=task_,
        context=context)

        return res