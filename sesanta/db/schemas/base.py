import abc
import typing

import pydantic
import pydantic_core
from bson import ObjectId
from pydantic.json_schema import JsonSchemaValue


class ObjectIdPydanticAnnotation:
    @classmethod
    def validate_object_id(cls, v: typing.Any, handler) -> ObjectId:
        if isinstance(v, ObjectId):
            return v

        s = handler(v)
        if ObjectId.is_valid(s):
            return ObjectId(s)
        msg = "Invalid ObjectId"
        raise ValueError(msg)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type,
        _handler,
    ) -> pydantic_core.core_schema.CoreSchema:
        return pydantic_core.core_schema.no_info_wrap_validator_function(
            cls.validate_object_id,
            pydantic_core.core_schema.str_schema(),
            serialization=pydantic_core.core_schema.to_string_ser_schema(),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        _core_schema,
        handler,
    ) -> JsonSchemaValue:
        return handler(pydantic_core.core_schema.str_schema())


class AbstractSchema(pydantic.BaseModel, abc.ABC):
    id: typing.Annotated[ObjectId, ObjectIdPydanticAnnotation] = pydantic.Field(
        default_factory=ObjectId,
    )
