# app/api/v1/schemas.py

import pydantic

class MovieRatingResponse(pydantic.BaseModel):
    omdb: dict
    tmdb: dict
    rotten_tomatoes: dict

class MovieReviewSource(pydantic.BaseModel):
    title:str
    rating: float | str | None
    year: int | str | None
    error: str | None