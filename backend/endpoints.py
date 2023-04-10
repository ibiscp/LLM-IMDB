import logging

from agent import MovieAgent
from database import MovieDatabase
from fastapi import APIRouter, HTTPException, Query
from run import get_result_and_thought_using_graph

# build router
router = APIRouter()
logger = logging.getLogger(__name__)
movie_graph = MovieDatabase()
agent_movie = MovieAgent.initialize(movie_graph=movie_graph)


@router.get("/predict")
def get_load(message: str = Query(...)):
    try:
        return get_result_and_thought_using_graph(agent_movie, movie_graph, message)
    except Exception as e:
        # Log stack trace
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e)) from e
