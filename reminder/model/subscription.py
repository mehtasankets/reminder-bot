from dataclasses import dataclass

@dataclass(frozen=True)
class Subscription():
    user_id: int
    username: str
    config_group_identity: str