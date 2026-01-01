from pydantic import BaseModel


class AppContext(BaseModel):

    # Whether to run the "full handshake" on the VFlex when adjusting.
    deep_adjust: bool
