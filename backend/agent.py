from langchain.agents.agent import AgentExecutor
from langchain.agents.mrkl.base import ZeroShotAgent
from langchain.agents.tools import Tool
from langchain.llms import OpenAI
from langchain.utilities.serpapi import SerpAPIWrapper
from movie_database_tool import LLMGraphChain

ZERO_SHOT_FORMAT_INSTRUCTIONS = """
Use the following format:

1. If similarity is 1.0, you know the answer is exactly what the user asked for.
2. If similarities are not equal to 1.0, you need to present the user with a list of similar movies, saying "Here are the movies that are similar to what you asked for".
3. If you find the movie title directly in the Search tool, you always need to look in the Movies_chain to check if that movie is in the graph database.

Instructions: 
a. Question: The input question you need to address.
b. Thought: Consider the appropriate course of action.
c. Action: Choose one of the available tools from [{tool_names}].
d. Action Input: Provide the input for the selected action.
e. Observation: Describe the outcome of the action.
(Note: Steps b to e may be repeated multiple times as needed.)

f. Thought: Indicate that the final answer is determined.
g. Final Answer: Provide the ultimate response to the original input question.
"""


class MovieAgent(AgentExecutor):
    """Movie agent"""

    @staticmethod
    def function_name():
        return "MovieAgent"

    @classmethod
    def initialize(cls, movie_graph, *args, **kwargs):
        llm = OpenAI(temperature=0)

        movie_tool = LLMGraphChain(llm=llm, graph=movie_graph, verbose=True)

        # Load the tool configs that are needed.
        search = SerpAPIWrapper()
        tools = [
            Tool(
                name="Movies_chain",
                func=movie_tool.run,
                description="Utilize this tool to search within a movie database, specifically designed to answer movie-related questions. The tool accepts inputs such as clear title, genre, director, actor, or year, ensuring accurate and targeted results. Ideal for inquiries that require information from one or more of the following categories: title, genre, director, actor, or year. This specialized tool offers streamlined search capabilities to help you find the movie information you need with ease.",
            ),
            Tool(
                name="Search",
                func=search.run,
                description="Use this tool when you need to gather broader or non-movie-specific information, such as finding the year a particular event occurred, researching historical context, searching for the year of nominated movies, or seeking other related data. After obtaining the necessary details, you can then use the movies_chain for more targeted movie information. This tool offers a wide range of search capabilities to help you find the answers you need on the internet.",
            ),
        ]

        agent = ZeroShotAgent.from_llm_and_tools(
            llm, tools, format_instructions=ZERO_SHOT_FORMAT_INSTRUCTIONS
        )

        return cls.from_agent_and_tools(agent=agent, tools=tools, verbose=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, *args, **kwargs):
        return super().run(*args, **kwargs)
