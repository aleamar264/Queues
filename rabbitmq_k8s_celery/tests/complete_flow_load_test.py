from locust import HttpUser, task, constant
import gevent
import requests
import locust
from random import choice, randint
import time
import asyncio
import httpx


def async_success(name, start_time, resp):
	locust.events.request.fire(
		request_type=resp.request.method,
		name=name,
		response_time=int((time.monotonic() - start_time) * 1000),
		response_length=len(resp.content),
	)


def async_failure(name, start_time, resp, message):
	locust.events.request.fire(
		request_type=resp.request.method,
		name=name,
		response_time=int((time.monotonic() - start_time) * 1000),
		exception=Exception(message),
	)


class ReportService(HttpUser):
	wait_time = constant(1)

	def _do_async_thing_handler(self, timeout: int = 600):
		# Request for a task
		choices = ["task_1", "task_2"]
		data = {"task": choice(choices), "name": f"random task {randint(1, 100)}"}
		url = "/test/"

		with httpx.Client() as client:
			# POST request to initiate task
			post_resp = client.post(url=self.host + url, json=data)
			if post_resp.status_code != 200:
				return
			task_id = post_resp.json().get("task_id")

			start_time = time.monotonic()
			end_time = start_time + timeout

			# Poll for task result
			while time.monotonic() < end_time:
				r = client.get(self.host + f"/test/task/{task_id}")
				if r.status_code == 200 and r.json().get("task_result") is not None:
					# Success logging (replace with Locust's success metrics)
					async_success("POST /test/ID - async", start_time, post_resp)

					return
				gevent.sleep(1)

			# Failure logging
		async_failure(
			"POST /test/ID - async",
			start_time,
			post_resp,
			f"Failed - timed out after {timeout} seconds",
		)

	@task
	def do_async_thing(self):
		gevent.spawn(self._do_async_thing_handler)
