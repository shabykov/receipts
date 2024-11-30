from pydantic import RootModel, ConfigDict


class UserId(RootModel):
    root: int

    model_config = ConfigDict(frozen=True)

    def int(self) -> int:
        return int(self.root)

    def string(self) -> str:
        return str(self.root)
