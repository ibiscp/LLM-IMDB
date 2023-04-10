from typing import Dict, List

from database import MovieDatabase
from langchain.chains.base import Chain
from langchain.chains.llm import LLMChain
from langchain.llms.base import BaseLLM
from langchain.prompts.base import BasePromptTemplate
from langchain.prompts.prompt import PromptTemplate
from pydantic import BaseModel, Extra

_PROMPT_TEMPLATE = """
You are helping to create a query for searching a graph database that finds similar movies based on specified parameters.
Your task is to translate the given question into a set of parameters for the query. Only include the information you were given.

The parameters are:
title (str, optional): The title of the movie
year (int, optional): The year the movie was released
genre (str, optional): The genre of the movie
director (str, optional): The director of the movie
actor (str, optional): The actor in the movie
same_attributes_as (optional): A dictionary of attributes to match the same attributes as another movie (optional)

Use the following format:
Question: "Question here"
Output: "Graph parameters here"

Example:
Question: "What is the title of the movie that was released in 2004 and directed by Steven Spielberg?"
Output:
year: 2004
director: Steven Spielberg

Question: "Movie with the same director as Eternal Sunshine of the Spotless Mind?"
Output:
same_attributes_as:
    director: Eternal Sunshine of the Spotless Mind

Begin!

Question: {question}
Output:
"""

PROMPT = PromptTemplate(input_variables=["question"], template=_PROMPT_TEMPLATE)


class LLMGraphChain(Chain, BaseModel):
    """Chain that interprets a prompt and executes python code to do math.

    Example:
        .. code-block:: python

            from langchain import LLMMathChain, OpenAI
            llm_math = LLMMathChain(llm=OpenAI())
    """

    llm: BaseLLM
    """LLM wrapper to use."""
    prompt: BasePromptTemplate = PROMPT
    """Prompt to use to translate to python if neccessary."""
    input_key: str = "question"  #: :meta private:
    output_key: str = "answer"  #: :meta private:
    graph: MovieDatabase

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Expect output key.

        :meta private:
        """
        return [self.output_key]

    def _process_llm_result(self, t: str) -> Dict[str, str]:
        import yaml

        self.callback_manager.on_text("\nQuery:\n", verbose=self.verbose)
        self.callback_manager.on_text(t, color="green", verbose=self.verbose)
        # Convert t to a dictionary
        t = yaml.safe_load(t)
        output = self.graph.query_movies(**t)
        self.callback_manager.on_text("\nAnswer: ", verbose=self.verbose)
        self.callback_manager.on_text(output, color="yellow", verbose=self.verbose)
        return {self.output_key: "\n".join([f"{i[0]}: {i[1]}" for i in output])}

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        llm_executor = LLMChain(
            prompt=self.prompt, llm=self.llm, callback_manager=self.callback_manager
        )
        self.callback_manager.on_text(inputs[self.input_key], verbose=self.verbose)
        t = llm_executor.predict(question=inputs[self.input_key], stop=["Output:"])
        return self._process_llm_result(t)

    @property
    def _chain_type(self) -> str:
        return "llm_movie_database"


if __name__ == "__main__":
    from langchain.llms import OpenAI

    llm = OpenAI(temperature=0.3)

    chain = LLMGraphChain(llm=llm, verbose=True)

    output = chain.run(
        "What is the title of the movie that was released in 2002 and directed by Steven Spielberg?"
    )

    print(output)
