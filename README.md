Build:

```
docker build . -t jobczyk2020-app
```

Run:

```
docker run --rm -d --restart always -p 28810:8888 jobczyk2020-app
```

App will be running at http://localhost:28810