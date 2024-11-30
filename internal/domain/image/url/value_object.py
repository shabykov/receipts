from pydantic import RootModel, ConfigDict


class URL(RootModel):
    root: str

    model_config = ConfigDict(frozen=True)

    def __str__(self):
        return str(self.root)

    def string(self) -> str:
        return str(self.root)
