## Strimzi, Faust

```shell
helm repo add strimzi https://strimzi.io/charts/
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo add kedacore https://kedacore.github.io/charts
helm repo update
helm install strimzi strimzi/strimzi-kafka-operator --create-namespace --namespace kafka
kubectl apply -f k8s/kafka.yaml -n kafka
helm install nginx-ingress ingress-nginx/ingress-nginx --namespace fastapi-test --create-namespace
helm install keda kedacore/keda --namespace keda --create-namespace
kubectl apply k8s/deployment
```

testing:

```shell title="Producer"
kubectl -n kafka run kafka-producer -ti --image=quay.io/strimzi/kafka:0.42.0-kafka-3.7.1 --rm=true --restart=Never -- bin/kafka-console-producer.sh --bootstrap-server my-cluster-kafka-bootstrap:9092 --topic my-topic
```

```shell title="Consumer"
kubectl -n kafka run kafka-consumer -ti --image=quay.io/strimzi/kafka:0.42.0-kafka-3.7.1 --rm=true --restart=Never -- bin/kafka-console-consumer.sh --bootstrap-server my-cluster-kafka-bootstrap:9092 --topic my-topic --from-beginning
```

To launch the command `$shell kubectl apply k8s/deployment`, that contain the fastapi, faust and redis, you need to wait that the `strimzi operator` and kafka is up. If you launch the other files, you will have an error 'cause they can connect to
service.

In this POC, we use strimzi (Kafka operator) and Faust (consumer), to process the data that is produce for and endpoint (like the integration services), this process, register and save the progress of the process (PROGRESS, PENDING, COMPLETE O FAILURE).
This create an UUID, that is used to track the progress of the task. The unique difference with RabbitMQ and Celery, is that, Celery create a task and assign a UUID and save in a DB like PostgreSQL o Redis, here we need to do this the manual way.

## Deployment

With only launch the helm chart (Kafka Opetator) we can not do anything, this only create the operator, to use kafka we need to launch a CDR's, this are inside of `k8s/kafka/kafka.yaml`, this file contains a `Kafka` kind, with the definition of the services. In this moment we are using kafka with `Zookeper`, but in the next releases we will use `Kraft`, the replace of `Zookeper` (Faust in this moment need `Zookeper` to work, I hope in next releases use `Kraft`).

```yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: my-cluster
spec:
  kafka:
    replicas: 3
    ...
    storage:
      type: jbod
      volumes:
        - id: 0
          type: persistent-claim
          size: 3Gi
          deleteClaim: false
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      auto.create.topics.enable: true
    ...
  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 2Gi
      deleteClaim: false
  ...
```

After launch this file, we need to wait a little, waiting the creation of the instances of `Kafka` and `Zookeper`. After that, we can launch the other files, like Python Server (`FastAPI`) and the consumer (`Faust`). This consumer work in a similar way like `Celery`.

## Testing

Using locust, we made a test of load, with 1000 of concurrent users, in this test, we don't have any fail (this is because we really didn't anything, only a wait of 10/15 seconds).

This test is only to know how is the behaviour of Faust and Strimzi.

![alt text](image/locust.png)

## Troubles

One of the problems here, was to create the `KEDA` with `Kafka`, the metrics are no well expose or I don't know how to expose this very well, so the `KEDA` file is created with a "lagThreshold" of 50 and 30 respective for each topic (task_1 and task_2).

The autoscaler is created (hpa) and the ScaledObject, but with a load of 1500-2000 concurrent users, this don't scale.

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: faust-scaler
  namespace: faust-workers
spec:
  scaleTargetRef:
    name: faust-worker
  minReplicaCount: 2
  maxReplicaCount: 10
  cooldownPeriod: 5
  pollingInterval: 10
  triggers:
    - type: kafka
      metadata:
        bootstrapServers: my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
        topic: task_1
        consumerGroup: my-streaming-consumer-group
        lagThreshold: "50" # Scale when lag exceeds 1000
        # offsetResetPolicy: "latest"
    - type: kafka
      metadata:
        bootstrapServers: my-cluster-kafka-bootstrap.kafka.svc.cluster.local:9092
        topic: task_2
        consumerGroup: my-streaming-consumer-group
        lagThreshold: "30" # Scale when lag exceeds 1000
        # offsetResetPolicy: "latest"
```
