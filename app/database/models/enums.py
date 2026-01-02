from enum import Enum


class CategoryName(str, Enum):
    work = "work"
    personal = "personal"
    study = "study"
    sport = "sport"
    other = "other"
