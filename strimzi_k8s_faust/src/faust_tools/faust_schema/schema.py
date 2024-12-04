from typing import Literal

from faust import Record


class Input(Record):
	name: str
	task: Literal["task_1", "task_2"]
	uuid: str
