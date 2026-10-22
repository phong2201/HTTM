from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, ConfigDict, model_serializer

ICT = timezone(timedelta(hours=7))

def to_ict(dt: datetime) -> str:
    if dt is None: return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(ICT).isoformat()

class ICTBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @model_serializer(mode='wrap')
    def serialize_datetime(self, handler):
        result = handler(self)
        for key, val in result.items():
            if isinstance(val, datetime):
                result[key] = to_ict(val)
        return result

class IMessageResponse(BaseModel):
    message: str