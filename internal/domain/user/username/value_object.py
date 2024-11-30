from pydantic import RootModel, ConfigDict


class Username(RootModel):
    root: str

    model_config = ConfigDict(frozen=True)

    def __str__(self):
        return str(self.root)

    def string(self) -> str:
        return str(self.root)
