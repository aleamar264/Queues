```shell
kubectl config get-contexts
kubectl config use-context docker-desktop
```

With docker and k8s plugin, you can easily deploy any application. The same images that you build
in docker are available for use in k8s.

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

```shell
kubectl apply -f k8s/deployment
kubectl port-forward service/rabbitmq 15672:15672
```

???+ warning
Be sure that the fastapi container is running in the host 0.0.0.0, in the other way you can't connect
to the service from other pods.

![locust_without_kde](image.png)
