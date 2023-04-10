import contextlib
import io
from typing import Dict

from logger import logger


def get_attributes_from_node(graph, title: str) -> Dict:
    """Get attributes from node"""
    attribute_dict = {"actors": [], "genre": [], "directors": [], "year": None}

    # Get attributes from node
    attribute_dict.update(**graph.nodes[title]["attributes"])

    # Add title
    attribute_dict["title"] = title

    for item, attr in graph[title].items():
        if attr["type"] == "title_year_edge":
            attribute_dict["year"] = item
        elif attr["type"] == "title_director_edge":
            attribute_dict["directors"].append(item)
        elif attr["type"] == "title_actor_edge":
            attribute_dict["actors"].append(item)
        elif attr["type"] == "title_genre_edge":
            attribute_dict["genre"].append(item)

    return attribute_dict


def get_result_and_thought_using_graph(
    langchain_object,
    database,
    message: str,
):
    """Get result and thought from extracted json"""
    try:
        if hasattr(langchain_object, "verbose"):
            langchain_object.verbose = True
        chat_input = None
        memory_key = ""
        if hasattr(langchain_object, "memory") and langchain_object.memory is not None:
            memory_key = langchain_object.memory.memory_key

        for key in langchain_object.input_keys:
            if key not in [memory_key, "chat_history"]:
                chat_input = {key: message}

        langchain_object.return_intermediate_steps = True

        with io.StringIO() as output_buffer, contextlib.redirect_stdout(output_buffer):
            try:
                output = langchain_object(chat_input)
                # output = {
                #     'movies': [
                #     {
                #     'actors': ['Leonardo DiCaprio', 'Tom Hanks', 'Christopher Walken', 'Martin Sheen'],
                #     'genre': ['Biography', 'Crime', 'Drama'],
                #     'directors': ['Steven Spielberg'],
                #     'year': 2002,
                #     'Poster': 'https://m.media-amazon.com/images/M/MV5BMTY5MzYzNjc5NV5BMl5BanBnXkFtZTYwNTUyNTc2.V1_UX67_CR0,0,67,98_AL.jpg',
                #     'Runtime': 141,
                #     'Rating': 8.1,
                #     'Overview': 'Barely 21 yet, Frank is a skilled forger who has passed as a doctor, lawyer and pilot. FBI agent Carl becomes obsessed with tracking down the con man, who only revels in the pursuit.',
                #     'title': 'Catch Me If You Can'
                #     },
                #     {
                #     'actors': ['Tom Cruise', 'Colin Farrell', 'Samantha Morton', 'Max von Sydow'],
                #     'genre': ['Action', 'Crime', 'Mystery'],
                #     'directors': ['Steven Spielberg'],
                #     'year': 2002,
                #     'Poster': 'https://m.media-amazon.com/images/M/MV5BZTI3YzZjZjEtMDdjOC00OWVjLTk0YmYtYzI2MGMwZjFiMzBlXkEyXkFqcGdeQXVyMTQxNzMzNDI@.V1_UX67_CR0,0,67,98_AL.jpg',
                #     'Runtime': 145,
                #     'Rating': 7.6,
                #     'Overview': 'In a future where a special police unit is able to arrest murderers before they commit their crimes, an officer from that unit is himself accused of a future murder.',
                #     'title': 'Minority Report'
                #     }
                #     ],
                #     'response': 'The movie released in 2002 and directed by Steven Spielberg is Catch Me If You Can and Minority Report.',
                #     'thought': 'Thought'
                # }
                # return output
            except ValueError as exc:
                # make the error message more informative
                logger.debug(f"Error: {str(exc)}")
                output = langchain_object.run(chat_input)

            intermediate_steps = [
                action[1]
                for action in output["intermediate_steps"]
                if action[0].tool == "Movies_chain"
            ][0]

            movie_names = build_dict(intermediate_steps)

            movies = [
                get_attributes_from_node(database.graph, movie)
                for movie in movie_names.keys()
            ]

            thought = output_buffer.getvalue().strip()

    except Exception as exc:
        raise ValueError(f"Error: {str(exc)}") from exc

    return {"movies": movies, "response": output["output"], "thought": thought}


def build_dict(input):
    pairs = input.split("\n")

    # Create an empty dictionary to store the pairs
    my_dict = {}

    # Iterate over each pair and add it to the dictionary
    for pair in pairs:
        # Split the pair into movie and rating using the colon character
        movie, rating = pair.split(": ")

        # Convert the rating to a float and add it to the dictionary
        my_dict[movie] = float(rating)

    return my_dict


def format_intermediate_steps(intermediate_steps):
    formatted_chain = "> Entering new AgentExecutor chain...\n"
    for step in intermediate_steps:
        action = step[0]
        observation = step[1]

        formatted_chain += (
            f" {action.log}\nAction: {action.tool}\nAction Input: {action.tool_input}\n"
        )
        formatted_chain += f"Observation: {observation}\n"

    final_answer = f"Final Answer: {observation}\n"
    formatted_chain += f"Thought: I now know the final answer\n{final_answer}\n"
    formatted_chain += "> Finished chain.\n"

    return formatted_chain
