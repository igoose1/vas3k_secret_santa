from utils.basic import User


class FindCycleUser(User):
    selected: set[str]
    location: str
