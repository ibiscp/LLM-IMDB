from typing import List, Optional, Tuple

import networkx as nx
import pandas as pd


class MovieDatabase:
    def __init__(self, csv_file: str = "data/imdb_top_1000.csv"):
        """Initialize the movie database"""

        # Process the csv file
        df = self.process_csv(csv_file)

        # Get the features
        years, genres, directors, actors, titles = self.get_features(df)

        # Create the graph
        self.graph = self.create_graph(years, genres, directors, actors, titles)

    def process_csv(self, csv_file: str):
        """Process the csv file"""

        # Read csv file
        df = pd.read_csv(csv_file)
        df.index = pd.RangeIndex(start=0, stop=len(df))

        # Drop columns
        df = df.drop(columns=["Certificate", "Meta_score", "No_of_Votes", "Gross"])

        # Rename columns
        df = df.rename(
            columns={
                "Series_Title": "Title",
                "Released_Year": "Year",
                "IMDB_Rating": "Rating",
                "Poster_Link": "Poster",
            }
        )

        # Drop line where Year is PG
        df = df[df["Year"] != "PG"]

        # Change runtime to only minutes and convert to int
        df["Runtime"] = df["Runtime"].str.replace("min", "")
        df["Runtime"] = df["Runtime"].astype(int)

        # Change year to int
        df["Year"] = df["Year"].astype(int)

        # Change rating to float
        df["Rating"] = df["Rating"].astype(float)

        # Change genre to list
        df["Genre"] = df["Genre"].str.split(", ")

        # Change director to list
        df["Director"] = df["Director"].str.split(", ")

        # Change actors to list
        df["Actors"] = df[["Star1", "Star2", "Star3", "Star4"]].values.tolist()

        # Drop columns
        df = df.drop(columns=["Star1", "Star2", "Star3", "Star4"])

        return df

    def get_features(self, df: pd.DataFrame):
        """Get the features from the dataframe"""

        def _extracted_from_get_features_8(df: pd.DataFrame, arg1: str):
            # Get all genres
            result = []
            for genre in df[arg1]:
                result.extend(genre)
            return set(result)

        # Get all titles
        titles = df.to_dict(orient="index")

        # Get all genres, directors, and actors
        genres = _extracted_from_get_features_8(df, "Genre")
        directors = _extracted_from_get_features_8(df, "Director")
        actors = _extracted_from_get_features_8(df, "Actors")

        # Get all years
        years = set(df["Year"])

        return years, genres, directors, actors, titles

    def create_graph(
        self, years: set, genres: set, directors: set, actors: set, titles: dict
    ):
        """Create a graph from the dataframe"""

        # Initialize the graph
        G = nx.Graph()

        def add_nodes_to_graph(graph, items, node_type):
            for item in items:
                graph.add_node(item, type=node_type)

        def add_edges_to_graph(graph, title, items, edge_type):
            for item in items:
                graph.add_edge(title, item, type=edge_type)

        # Add years, genres, directors, and actors nodes
        add_nodes_to_graph(G, years, "year")
        add_nodes_to_graph(G, genres, "genre")
        add_nodes_to_graph(G, directors, "director")
        add_nodes_to_graph(G, actors, "actor")

        # Iterate through the list of dictionaries and add nodes and edges
        for movie in titles.values():
            genre = movie.pop("Genre")
            director = movie.pop("Director")
            actor = movie.pop("Actors")
            year = movie.pop("Year")
            title = movie.pop("Title")

            # Add title node
            G.add_node(title, type="title", attributes=movie)

            # Add year node and edge
            G.add_node(year, type="year")
            G.add_edge(title, year, type="title_year_edge")

            # Add edges for directors, actors, and genres
            add_edges_to_graph(G, title, director, "title_director_edge")
            add_edges_to_graph(G, title, actor, "title_actor_edge")
            add_edges_to_graph(G, title, genre, "title_genre_edge")

        return G

    def query_movies(
        self,
        title: Optional[str] = None,
        year: Optional[int] = None,
        genre: Optional[str] = None,
        director: Optional[str] = None,
        actor: Optional[str] = None,
        same_attributes_as: Optional[dict[str, str]] = None,
    ) -> List[Tuple[str, float]]:
        def get_neighbors_by_edge_type(node, edge_type):
            return [
                neighbor
                for neighbor, edge_attrs in self.graph[node].items()
                if edge_attrs["type"] == edge_type
            ]

        def matches_partial(queried, neighbor):
            if isinstance(queried, int) and isinstance(neighbor, int):
                return queried == neighbor
            elif isinstance(queried, str) and isinstance(neighbor, str):
                for q in queried.split():
                    if q.lower() in neighbor.lower():
                        return True
            return False

        def similarity_score(title, queried_attributes):
            matching_attributes = sum(
                any((matches_partial(attr, n) for n in self.graph.neighbors(title)))
                for attr in queried_attributes
            )
            return matching_attributes / len(queried_attributes)

        queried_attributes = []
        if year:
            queried_attributes.append(year)
        if genre:
            queried_attributes.append(genre)
        if director:
            queried_attributes.append(director)
        if actor:
            queried_attributes.append(actor)

        if same_attributes_as:
            for key, value in same_attributes_as.items():
                queried_attributes.extend(
                    get_neighbors_by_edge_type(
                        self.graph, value, f"title_{key}_edself.graphe"
                    )
                )

        if title:
            queried_attributes.extend(
                get_neighbors_by_edge_type(title, "title_year_edge")
            )
            queried_attributes.extend(
                get_neighbors_by_edge_type(title, "title_genre_edge")
            )
            queried_attributes.extend(
                get_neighbors_by_edge_type(title, "title_director_edge")
            )
            queried_attributes.extend(
                get_neighbors_by_edge_type(title, "title_actor_edge")
            )

        movie_scores = [
            (m, similarity_score(m, queried_attributes))
            for m, data in self.graph.nodes(data=True)
            if data["type"] == "title"
        ]
        movie_scores = [(m, s) for m, s in movie_scores if s > 0]
        movie_scores.sort(key=lambda x: x[1], reverse=True)

        # Keep only score 1 if exists
        if any(s == 1 for m, s in movie_scores):
            movie_scores = [(m, s) for m, s in movie_scores if s == 1]

        return movie_scores[:5]


if __name__ == "__main__":
    database = MovieDatabase()

    a = database.graph.nodes["The Dark Knight"]

    print(a)
