import time
from random import choice, randint

import locust
from locust import FastHttpUser, constant, task


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


class ReportService(FastHttpUser):
	wait_time = constant(1)

	@task
	def _do_async_thing_handler(self, timeout: int = 600):
		# Request for a task
		choices = ["task_1", "task_2"]
		data = {"task": choice(choices), "name": f"random task {randint(1, 100)}"}
		url = "/test/"
		# POST request to initiate task
		resp = self.client.post(url, json=data)
		if resp.status_code != 200:
			return
		task_id = resp.json().get("uuid")

		start_time = time.monotonic()
		end_time = start_time + timeout

		# Poll for task result
		while time.monotonic() < end_time:
			r = self.client.get(f"/test/task/{task_id}")
			if r.status_code == 200 and r.json().get("task_result") is not None:
				# Success logging (replace with Locust's success metrics)
				async_success("POST /report/ID - async", start_time, resp)
				return
			time.sleep(1)
		async_failure(
			"POST /report/ID - async",
			start_time,
			resp,
			"Failed - timed out after %s seconds" % timeout,
		)
		# Failure logging
