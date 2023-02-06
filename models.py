import typing
from pydantic import BaseModel, Extra, constr


class Km(BaseModel, extra=Extra.forbid):
    kit: constr(min_length=31)
    article: str


class InsertKitModel(BaseModel, extra=Extra.forbid):
    data: list[Km]


class ArticleModel(BaseModel, extra=Extra.forbid):
    data: list[str]


class SimpleAnswer(BaseModel, extra=Extra.forbid):
    status: bool = True


class IntegrityAnswer(BaseModel, extra=Extra.forbid):
    status: bool = True
    data: list[typing.Any]
    integrity: bool


class CountArticlesAnswer(BaseModel, extra=Extra.forbid):
    status: bool = True
    quantity: int


class DeleteAnswer(BaseModel):
    status: bool = True
    deleted: int
