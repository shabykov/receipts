from pydantic import RootModel, ConfigDict, UUID4


class ReceiptUUID(RootModel):
    root: UUID4

    model_config = ConfigDict(frozen=True)

    def __str__(self):
        return str(self.root)

    def string(self) -> str:
        return str(self.root)
