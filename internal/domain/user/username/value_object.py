from pydantic import RootModel, ConfigDict


class Username(RootModel):
    root: str

    model_config = ConfigDict(frozen=True)

    def string(self) -> str:
        return str(self.root)
