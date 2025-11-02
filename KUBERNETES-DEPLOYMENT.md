# Kubernetes Deployment Instructions

## Complete Guide to Deploy Barista App on Docker Desktop Kubernetes

---

## Part 1: Prerequisites

### 1. Enable Kubernetes in Docker Desktop

1. Open **Docker Desktop**
2. Click **Settings** (gear icon)
3. Go to **Kubernetes** tab
4. Check **Enable Kubernetes**
5. Click **Apply & Restart**
6. Wait for Kubernetes to start (green indicator)

### 2. Verify Kubernetes is Running

Open terminal/command prompt and run:

```bash
kubectl version --client
kubectl cluster-info
```

You should see Kubernetes cluster information.

---

## Part 2: Build Docker Images

### On Windows:

```cmd
build-images.bat
```

### On Mac/Linux:

```bash
chmod +x build-images.sh
./build-images.sh
```

### What This Does:
- Builds `barista-backend:latest` from `./backend/Dockerfile`
- Builds `barista-frontend:latest` from `./frontend/Dockerfile`
- Images are stored locally in Docker Desktop

### Verify Images:

```bash
docker images | grep barista
```

You should see:
```
barista-backend    latest    ...    ...    ...
barista-frontend   latest    ...    ...    ...
```

---

## Part 3: Update Secrets (IMPORTANT!)

Edit `k8s/backend-secret.yaml` and replace placeholder values with your actual credentials:

```yaml
stringData:
  AWS_ACCESS_KEY_ID: "your_actual_aws_key"
  AWS_SECRET_ACCESS_KEY: "your_actual_aws_secret"
  GOOGLE_API_KEY: "your_actual_google_api_key"
  SECRET_KEY: "your_actual_secret_key"
  SMTP_USER: "your_email@gmail.com"
  SMTP_PASSWORD: "your_app_password"
  SLACK_WEBHOOK_URL: "your_slack_webhook_url"
```

---

## Part 4: Deploy to Kubernetes

### Deploy All Resources:

```bash
kubectl apply -f k8s/
```

This creates:
- ✅ Namespace: `barista-app`
- ✅ PostgreSQL with persistent storage
- ✅ Backend API (2 replicas)
- ✅ Frontend (2 replicas)
- ✅ Services (LoadBalancer)

---

## Part 5: Monitor Deployment

### Check Pod Status:

```bash
kubectl get pods -n barista-app
```

Wait until all pods show `Running`:

```
NAME                        READY   STATUS    RESTARTS   AGE
postgres-xxx-xxx            1/1     Running   0          2m
backend-xxx-xxx             1/1     Running   0          1m
backend-xxx-xxx             1/1     Running   0          1m
frontend-xxx-xxx            1/1     Running   0          1m
frontend-xxx-xxx            1/1     Running   0          1m
```

### Watch Pods in Real-Time:

```bash
kubectl get pods -n barista-app -w
```

Press `Ctrl+C` to stop watching.

---

## Part 6: Access the Application

Once all pods are `Running`:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## Common Commands

### View All Resources:
```bash
kubectl get all -n barista-app
```

### View Logs:
```bash
# Backend logs
kubectl logs -n barista-app -l app=backend --tail=50

# Frontend logs
kubectl logs -n barista-app -l app=frontend --tail=50

# PostgreSQL logs
kubectl logs -n barista-app -l app=postgres --tail=50
```

### Restart Deployment:
```bash
kubectl rollout restart deployment/backend -n barista-app
kubectl rollout restart deployment/frontend -n barista-app
```

### Delete Everything:
```bash
kubectl delete namespace barista-app
```

---

## Troubleshooting

### Issue: Pods stuck in "Pending"

**Check:**
```bash
kubectl describe pod -n barista-app <pod-name>
```

**Common causes:**
- Insufficient resources
- Image not found

### Issue: Pods in "ImagePullBackOff"

**Solution:**
1. Verify images exist:
   ```bash
   docker images | grep barista
   ```

2. Rebuild images:
   ```bash
   ./build-images.sh
   ```

3. Delete and recreate pods:
   ```bash
   kubectl delete pod -n barista-app -l app=backend
   kubectl delete pod -n barista-app -l app=frontend
   ```

### Issue: Cannot access http://localhost:3000

**Check services:**
```bash
kubectl get svc -n barista-app
```

**Port forward manually:**
```bash
kubectl port-forward -n barista-app svc/frontend 3000:3000
kubectl port-forward -n barista-app svc/backend 8000:8000
```

---

## Next Steps

1. ✅ Build images
2. ✅ Update secrets
3. ✅ Deploy to Kubernetes
4. ✅ Access application
5. 🎉 Start using your AI Barista!

For detailed documentation, see `k8s/README.md`
