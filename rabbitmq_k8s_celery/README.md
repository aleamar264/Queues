# RabbitMQ - Celery - K8S

Like in this project we are using K8S, we will use the context given by `Docker`, using docker desktop and enabling the option of K8S.

```shell
kubectl config get-contexts
kubectl config use-context docker-desktop
```

With docker and k8s plugin, you can easily deploy any application. The same images that you build in docker are available for use in k8s.
To facilitate the deploying of serveral applications, we will use helm, with helm the application already had several configuration in it,
only is tunning some parameters.

We will use the charts for, `nginx`, `keda`, `rabbitmq`.

```shell
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add kedacore https://kedacore.github.io/charts
helm upgrade --install rabbitmq  bitnami/rabbitmq -f k8s/helm/rabbitmq.yaml
helm repo update
helm upgrade --install nginx-ingress ingress-nginx/ingress-nginx --namespace fastapi-test --create-namespace
helm repo update
helm install keda kedacore/keda --namespace keda --create-namespace

```

The other files to deploy in K8S are in the `K8S` folder.

```shell
kubectl apply -f k8s/deployment
kubectl port-forward service/rabbitmq 15672:15672
```

???+ warning
Be sure that the fastapi container is running in the host 0.0.0.0, in the other way you can't connect
to the service from other pods.

Here we use the famous duo `RabbitMQ` and `Celery` to queue the data and process in parallel. To extend more the
capabilities, we use `KEDA` to scale the numbers of pods that controller `Celery`, this grow with the number of
data in the queue (length). With minimum 2 pods and max 30.

The length of the Queue can be modify in the file of `K8S/deployment/celery_keda.yaml`

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: celery-worker-scaler
  namespace: celery-workers
spec:
  scaleTargetRef:
    name: celery-worker
  pollingInterval: 3 #(1)!
  minReplicaCount: 2 #(2)!
  maxReplicaCount: 30 #(3)!
  triggers:
    - type: rabbitmq
      metadata:
        queueName: Test_Query
        queueLength: "1000"
      authenticationRef:
        name: rabbitmq-worker-trigger
```

1. The frequency with the keda refresh the data about the `queueLength`
2. Minimun replica count.
3. Maximum replica count.

## Implementation

Implement `Celery` and `RabbitMQ` is relative easy and had a lot of documentation and tutorials on internet.

The configuration of `Celery` is divided in 2:

1. Broker, result backend and Querys to use.
2. The configuration of `Celery`.

=== "Broker, Result and Backend"

```python
class BaseConfig:
CELERY_BROKER_URL: str = os.environ.get(
"CELERY_BROKER_URL",
"amqp://rabbitmq:rabbitmq@rabbitmq-headless.default.svc.cluster.local:5672//",
)
CELERY_RESULT_BACKEND: str = os.environ.get(
"CELERY_RESULT_BACKEND", "redis://redis.default.svc.cluster.local:6379/0"
)

        CELERY_TASK_QUEUES: tuple[Queue, Queue] = (
            # default queue
            Queue("celery"),
            # custom queue
            Queue("Test_Query"),
        )

        CELERY_TASK_ROUTES = (route_task,)

```

=== "Celery Configuration"

```python
def create_celery() -> Proxy:
    # register_pydantic_model()
    celery_app = current_celery_app
    celery_app.config_from_object(settings, namespace="CELERY")
    celery_app.conf.update(task_track_started=True)
    # celery_app.conf.update(task_serializer="pydantic")
    # celery_app.conf.update(result_serializer="pydantic")
    # celery_app.conf.update(event_serializer="pydantic")
    celery_app.conf.update(task_serializer="json")
    celery_app.conf.update(result_serializer="json")
    celery_app.conf.update(event_serializer="json")
    celery_app.conf.update(
        accept_content=["application/json", "application/x-pydantic"]
    )
    celery_app.conf.update(
        result_accept_content=["application/json", "application/x-pydantic"]
    )
    celery_app.conf.update(worker_concurrency=1)
    celery_app.conf.update(worker_max_tasks_per_child=100)
    celery_app.conf.update(worker_heartbeat=120)
    celery_app.conf.update(result_expires=200)
    celery_app.conf.update(result_persistent=True)
    celery_app.conf.update(enable_utc=True)
    celery_app.conf.update(worker_send_task_events=False)
    celery_app.conf.update(worker_prefetch_multiplier=2)
    celery_app.conf.update(task_acks_late=True)
    celery_app.conf.update(task_reject_on_worker_lost=True)
    celery_app.conf.update(broker_pool_limit=5)

    register_pydantic_types(Input, Ouput)

    return celery_app
```

Like we are using `FastAPI`, we can instantiate the `Celery` app like an "state" of `FastAPI`.

```python
from fastapi import FastAPI

from celery_tools.config.celery_utils import create_celery
from routes.intregration import router

app = FastAPI()
app.celery_app = create_celery()  # type: ignore
app.include_router(router)

celery = app.celery_app  # type: ignore
```

And call the `Celery` app from the worker.

## Worker

We only need to call the command `celery` that give the package of `Celery` in python.

Like you can see we call the `celery` variable that we create in the main file.

```sh
#!/bin/bash

set -o errexit
set -o nounset

celery -A main.celery worker --loglevel=info -Q Test_Query
```

## Load Test

We use `Locust` to create a load test.

The test that we use came from [Scaling Celery workers with RabbitMQ on Kubernetes](https://learnk8s.io/scaling-celery-rabbitmq-kubernetes) with some tweaks to own case.

![Locust](image/locust.png)

The resources assigned to `FastAPI` are:

```yaml
resources:
    requests:
    cpu: "1"
    memory: "1Gi"
    limits:
    cpu: "2"
    memory: "2Gi"
```

The resources for `Celery`:

```yaml
resources:
  requests:
    cpu: "500m"
    memory: "500Mi"
  limits:
    cpu: "1"
    memory: "1Gi"
```

![RabbitMQ](image/rabbitmq.png)

Like `Locust` use a significant amount of resources, we run locust outside of the cluster, for that reason we use `NGINX` to expose the port of `FastAPI` application to 80 in localhost.

The test is "beautiful" 'cause we simulated the process, so all the calls are succeed, but with this we can had some approach to how is the behaviour with `7000` concurrent users.
