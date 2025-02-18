from dataclasses import dataclass, fields, is_dataclass, asdict
from typing import Any, Self
from datetime import datetime
import uuid

JSON: type = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


@dataclass
class BaseModel:
    @classmethod
    def from_dict(cls, data: dict) -> Self:
        kwargs = {}
        try:
            for field in fields(cls):
                field_name = field.name
                field_type = field.type

                if field_name not in data:
                    continue

                value = data[field_name]

                if isinstance(value, dict) and hasattr(field_type, "from_dict"):
                    kwargs[field_name] = field_type.from_dict(value)

                elif isinstance(value, list):
                    elem_type = field_type.__args__[0]
                    kwargs[field_name] = [
                        elem_type.from_dict(v) if isinstance(v, dict) else v
                        for v in value
                    ]

                elif field_type == datetime and isinstance(value, str):
                    kwargs[field_name] = datetime.fromisoformat(value.rstrip("Z"))

                else:
                    kwargs[field_name] = value
        except Exception as e:
            print(f"Erroroccured in {field_name}, which type is {field_type}")
            raise e

        return cls(**kwargs)

    def to_dict(obj: Any) -> dict:
        def convert_value(value):
            if isinstance(value, datetime):
                return value.isoformat() + "Z"
            elif is_dataclass(value):
                return asdict(value)
            elif isinstance(value, list):
                return [convert_value(v) for v in value]
            return value

        return {key: convert_value(value) for key, value in asdict(obj).items()}


@dataclass
class BaseDocument(BaseModel):
    name: str = ""
    id: str = str(uuid.uuid4())
    issue_date: str = datetime.now()
    version: str = "0.0"
    department: str = ""
    responsible_person: str = ""
