from typing import Optional

from pydantic import BaseModel

class UserIntent(BaseModel):
    location:Optional[str]=None
    activity:Optional[str]=None
    intent:Optional[str]=None
    transport:Optional[str]=None
    user_group:Optional[str]=None
    time: Optional[str]=None