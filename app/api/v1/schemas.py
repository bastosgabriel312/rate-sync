# app/api/v1/schemas.py

import pydantic

class MovieRatingResponse(pydantic.BaseModel):
    omdb: dict
    tmdb: dict
    rotten_tomatoes: dict