# app/api/v1/routes.py

from datetime import datetime, timezone

from fastapi import WebSocket, WebSocketDisconnect

from starlette.websockets import WebSocketState
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, HTTPException, Depends

from app.domain.use_cases.find_movie import FindMovie
from app.domain.use_cases.get_more_populars import GetMorePopulars
from app.domain.use_cases.get_movie_ratings import GetMovieRatings
from app.infrastructure.api_clients.letterboxd_client import LetterBoxdClient
from app.infrastructure.api_clients.cinemeta_client import CinemetaClient
from app.infrastructure.api_clients.omdb_client import OMDBClient
from app.core.monitor import all_metrics

router = APIRouter()

cinemeta_client = CinemetaClient()
omdb_client = OMDBClient()
letterboxd_client = LetterBoxdClient()

get_movie_ratings_use_case = GetMovieRatings(cinemeta_client, omdb_client, letterboxd_client)
get_more_populars_use_case = GetMorePopulars(cinemeta_client)
find_movie_use_case = FindMovie(cinemeta_client)

def get_movie_ratings_service() -> GetMovieRatings:
    return get_movie_ratings_use_case

def get_more_populars_service() -> GetMorePopulars:
    return get_more_populars_use_case

def find_movie_service() -> FindMovie:
    return find_movie_use_case

@router.get("/health")
async def health():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }

@router.get("/ratings/{movie_id}")
async def get_movie_ratings(movie_id: str, service: GetMovieRatings = Depends(get_movie_ratings_service)):
    try:
        ratings = await service.execute(movie_id)
        return ratings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/more_populars")
async def get_more_populars(service: GetMorePopulars = Depends(get_more_populars_service)):
    try:
        populars = await service.execute()
        return populars
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/movie/")
async def find_movie(movie_title: str, service: FindMovie = Depends(find_movie_service)):
    try:
        movie = await service.execute(movie_title)
        return movie
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/find_movie/")
async def websocket_find_movie(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            movie_title = await websocket.receive_text()
            try:
                movie = await find_movie_use_case.execute(movie_title)
                await websocket.send_json(jsonable_encoder(movie))
            except Exception as e:
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json({"error": str(e)})
                break
    except WebSocketDisconnect:
        print("WebSocket desconectado")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        await websocket.close()


@router.get("/metrics")
async def metrics():
    """Return in-memory metrics counters for quick operational insight.

    Note: lightweight in-memory counters only for dev/local monitoring.
    """
    try:
        return all_metrics()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
