# Kubernetes Deployment Guide for Barista Agentic App

This guide will help you deploy the Barista Agentic App to Kubernetes on Docker Desktop.

## Prerequisites

1. **Docker Desktop** installed and running
2. **Kubernetes enabled** in Docker Desktop:
   - Open Docker Desktop
   - Go to Settings → Kubernetes
   - Check "Enable Kubernetes"
   - Click "Apply & Restart"
3. **kubectl** command-line tool (comes with Docker Desktop)

## Quick Start

### Step 1: Build Docker Images

Run the build script from the project root:

**On Windows:**
```cmd
build-images.bat
```

**On Mac/Linux:**
```bash
chmod +x build-images.sh
./build-images.sh
```

This will build:
- `barista-backend:latest`
- `barista-frontend:latest`

### Step 2: Update Secrets

Edit `k8s/backend-secret.yaml` and replace with your actual credentials:

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

### Step 3: Deploy to Kubernetes

From the project root, run:

```bash
kubectl apply -f k8s/
```

This will create:
- Namespace: `barista-app`
- PostgreSQL database with persistent storage
- Backend API (2 replicas)
- Frontend web app (2 replicas)
- Services for external access

### Step 4: Wait for Pods to be Ready

Check deployment status:

```bash
kubectl get pods -n barista-app
```

Wait until all pods show `Running` status (may take 2-3 minutes):

```
NAME                        READY   STATUS    RESTARTS   AGE
postgres-xxxxxxxxx-xxxxx    1/1     Running   0          2m
backend-xxxxxxxxx-xxxxx     1/1     Running   0          1m
backend-xxxxxxxxx-xxxxx     1/1     Running   0          1m
frontend-xxxxxxxxx-xxxxx    1/1     Running   0          1m
frontend-xxxxxxxxx-xxxxx    1/1     Running   0          1m
```

### Step 5: Access the Application

Once all pods are running:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Useful Commands

### Check All Resources
```bash
kubectl get all -n barista-app
```

### View Pod Logs
```bash
# Backend logs
kubectl logs -n barista-app -l app=backend --tail=100 -f

# Frontend logs
kubectl logs -n barista-app -l app=frontend --tail=100 -f

# PostgreSQL logs
kubectl logs -n barista-app -l app=postgres --tail=100 -f
```

### Describe a Pod (for troubleshooting)
```bash
kubectl describe pod -n barista-app <pod-name>
```

### Execute Commands in a Pod
```bash
# Access backend shell
kubectl exec -it -n barista-app <backend-pod-name> -- /bin/bash

# Access PostgreSQL
kubectl exec -it -n barista-app <postgres-pod-name> -- psql -U barista -d baristadb
```

### Restart Deployments
```bash
# Restart backend
kubectl rollout restart deployment/backend -n barista-app

# Restart frontend
kubectl rollout restart deployment/frontend -n barista-app
```

### Scale Deployments
```bash
# Scale backend to 3 replicas
kubectl scale deployment/backend -n barista-app --replicas=3

# Scale frontend to 3 replicas
kubectl scale deployment/frontend -n barista-app --replicas=3
```

### Delete Everything
```bash
# Delete all resources
kubectl delete namespace barista-app

# Or delete specific resources
kubectl delete -f k8s/
```

## Troubleshooting

### Pods Not Starting

1. **Check pod status:**
   ```bash
   kubectl get pods -n barista-app
   ```

2. **View pod events:**
   ```bash
   kubectl describe pod -n barista-app <pod-name>
   ```

3. **Check logs:**
   ```bash
   kubectl logs -n barista-app <pod-name>
   ```

### Image Pull Errors

If you see `ImagePullBackOff` or `ErrImagePull`:

1. Verify images exist locally:
   ```bash
   docker images | grep barista
   ```

2. Rebuild images:
   ```bash
   ./build-images.sh  # or build-images.bat on Windows
   ```

3. Restart the deployment:
   ```bash
   kubectl rollout restart deployment/<deployment-name> -n barista-app
   ```

### Database Connection Issues

1. **Check PostgreSQL is running:**
   ```bash
   kubectl get pods -n barista-app -l app=postgres
   ```

2. **Test database connection:**
   ```bash
   kubectl exec -it -n barista-app <postgres-pod-name> -- psql -U barista -d baristadb -c "SELECT 1;"
   ```

3. **Check backend can reach database:**
   ```bash
   kubectl logs -n barista-app -l app=backend | grep -i database
   ```

### Cannot Access Application

1. **Check services:**
   ```bash
   kubectl get svc -n barista-app
   ```

2. **Verify LoadBalancer services have external IPs:**
   ```
   NAME       TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)
   frontend   LoadBalancer   10.96.x.x       localhost     3000:xxxxx/TCP
   backend    LoadBalancer   10.96.x.x       localhost     8000:xxxxx/TCP
   ```

3. **Port forward if LoadBalancer not working:**
   ```bash
   # Frontend
   kubectl port-forward -n barista-app svc/frontend 3000:3000
   
   # Backend
   kubectl port-forward -n barista-app svc/backend 8000:8000
   ```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Desktop                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │              Kubernetes Cluster                    │  │
│  │                                                     │  │
│  │  ┌──────────────┐  ┌──────────────┐              │  │
│  │  │   Frontend   │  │   Backend    │              │  │
│  │  │  (2 replicas)│  │  (2 replicas)│              │  │
│  │  │  Port: 3000  │  │  Port: 8000  │              │  │
│  │  └──────┬───────┘  └──────┬───────┘              │  │
│  │         │                  │                       │  │
│  │         │                  │                       │  │
│  │         │                  ▼                       │  │
│  │         │          ┌──────────────┐               │  │
│  │         │          │  PostgreSQL  │               │  │
│  │         │          │  (1 replica) │               │  │
│  │         │          │  Port: 5432  │               │  │
│  │         │          └──────┬───────┘               │  │
│  │         │                  │                       │  │
│  │         │                  ▼                       │  │
│  │         │          ┌──────────────┐               │  │
│  │         │          │ Persistent   │               │  │
│  │         │          │   Volume     │               │  │
│  │         │          └──────────────┘               │  │
│  └─────────┼──────────────────────────────────────────┘  │
│            │                                              │
└────────────┼──────────────────────────────────────────────┘
             │
             ▼
      http://localhost:3000 (Frontend)
      http://localhost:8000 (Backend)
```

## Resource Limits

| Component  | CPU Request | CPU Limit | Memory Request | Memory Limit |
|------------|-------------|-----------|----------------|--------------|
| PostgreSQL | 250m        | 500m      | 256Mi          | 512Mi        |
| Backend    | 500m        | 1000m     | 512Mi          | 1Gi          |
| Frontend   | 250m        | 500m      | 256Mi          | 512Mi        |

**Total Resources Required:**
- CPU: ~2 cores
- Memory: ~3GB

## Updating the Application

### Code Changes

1. **Make your code changes**

2. **Rebuild images:**
   ```bash
   ./build-images.sh  # or build-images.bat
   ```

3. **Restart deployments:**
   ```bash
   kubectl rollout restart deployment/backend -n barista-app
   kubectl rollout restart deployment/frontend -n barista-app
   ```

### Configuration Changes

1. **Edit ConfigMap or Secret:**
   ```bash
   kubectl edit configmap backend-config -n barista-app
   # or
   kubectl edit secret backend-secret -n barista-app
   ```

2. **Restart affected pods:**
   ```bash
   kubectl rollout restart deployment/backend -n barista-app
   ```

## Monitoring

### Watch Pod Status
```bash
kubectl get pods -n barista-app -w
```

### View Resource Usage
```bash
kubectl top pods -n barista-app
kubectl top nodes
```

### Check Events
```bash
kubectl get events -n barista-app --sort-by='.lastTimestamp'
```

## Cleanup

To completely remove the application:

```bash
# Delete all resources
kubectl delete namespace barista-app

# Verify deletion
kubectl get all -n barista-app
```

Note: This will delete all data including the PostgreSQL database!

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review pod logs: `kubectl logs -n barista-app <pod-name>`
3. Check pod events: `kubectl describe pod -n barista-app <pod-name>`
