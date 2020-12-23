Build:

```
docker build . -t jobczyk2020-app
```

Run:

![Docker Build](https://github.com/kstawiski/jobczyk2020-app/workflows/Docker%20Build/badge.svg)

```
docker run --name jobczyk2020-app -d --restart always -p 28810:8888 kstawiski/jobczyk2020-app
```

App will be running at http://localhost:28810
