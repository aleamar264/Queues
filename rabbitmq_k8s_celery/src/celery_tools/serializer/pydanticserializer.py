import json
from functools import partial
from typing import Any

from kombu.utils.json import register_type  # type: ignore
from pydantic import BaseModel

import schemas


class PydanticSerializer(json.JSONEncoder):
    def default(self, obj: Any) -> dict[str, Any] | Any:
        if isinstance(obj, BaseModel):
            return obj.model_dump() | {"__type__": type(obj).__name__}
        else:
            return json.JSONEncoder.default(self, obj)


def pydantic_decoder(obj: Any) -> Any:
    if "__type__" in obj:
        if obj["__type__"] in dir(schemas):
            cls = getattr(schemas, obj["__type__"])
            return cls.parse_obj(obj)
    return obj


def pydantic_dupms(obj: dict[str, Any]) -> str:
    return json.dumps(obj, cls=PydanticSerializer)


def pydantic_loads(obj: str) -> Any:
    return json.loads(obj, object_hook=pydantic_decoder)


# zeroohub solution


def class_full_name(clz: type[BaseModel]) -> str:
    return ".".join([clz.__module__, clz.__qualname__])


def _encoder(obj: BaseModel, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return obj.model_dump(*args, **kwargs)


def _decoder(clz: type[BaseModel], data: dict[str, Any]) -> BaseModel:
    return clz.model_validate(data)


def register_pydantic_types(*models: type[BaseModel]) -> None:
    for model in models:
        register_type(
            model,
            class_full_name(model),
            encoder=_encoder,
            decoder=partial(_decoder, model),
        )
