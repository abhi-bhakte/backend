from pydantic import BaseModel, Field
from typing import List, Dict
from bson import ObjectId

# Support for ObjectId in Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class ModulePermissions(BaseModel):
    module: str
    permissions: List[str]

class PermissionModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId = Field(..., description="MongoDB ObjectId of the user")
    modules: Dict[str, List[str]]  # e.g., { "dashboard": ["read", "write"] }

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
