from typing import Literal

from pydantic import BaseModel


class Input(BaseModel):
	task: Literal["task_1", "task_2"]
	name: str
	uuid: str | None = None


class Output(BaseModel):
	name_task: str
	state: str
