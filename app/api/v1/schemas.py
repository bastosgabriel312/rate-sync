# app/api/v1/schemas.py

import pydantic

class MovieReviewSource(pydantic.BaseModel):
    title: str | None = None
    rating: float | str | None = None
    year: int | str | None = None
    error: str | None = None

class MovieRatingResponse(pydantic.BaseModel):
    cinemeta: MovieReviewSource | dict[str, str]
    omdb: list[dict] | dict[str, str]
    letterboxd: MovieReviewSource | dict[str, str]