# Deployment Guide

Complete guide for deploying the Document Processing Application with Docker.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+
- OpenAI API Key

## Quick Start

### Option 1: Automated Setup (Recommended)

Run the automated setup script:

```bash
./scripts/setup-docker.sh
```

This will:

1. Check Docker installation
2. Create `.env` file from template
3. Prompt for API key configuration
4. Build and start all containers
5. Run health checks

### Option 2: Manual Setup

**Step 1: Configure Environment**

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

**Step 2: Start Services**

Development mode (with logs):

```bash
docker-compose up --build
```

Or detached mode:

```bash
docker-compose up -d --build
```

Production mode:

```bash
docker-compose -f docker-compose.prod.yml up -d --build
```

**Step 3: Verify Deployment**

Check service status:

```bash
docker-compose ps
```

Test endpoints:

```bash
curl http://localhost:8000/
curl http://localhost/
```

## Access Points

| Service  | URL                        | Description                   |
| -------- | -------------------------- | ----------------------------- |
| Frontend | http://localhost           | React UI                      |
| Backend  | http://localhost:8000      | FastAPI server                |
| API Docs | http://localhost:8000/docs | Interactive API documentation |

## Management Commands

### Using Makefile

```bash
make help          # Show all available commands
make build         # Build all Docker images
make up            # Start services (detached)
make down          # Stop all services
make logs          # View logs from all services
make restart       # Restart all services
make clean         # Stop services and remove volumes
make dev           # Start in development mode (with logs)
make prod          # Start in production mode
make test          # Run tests in Docker container
make backend-logs  # View backend logs only
make frontend-logs # View frontend logs only
make backend-shell # Access backend container shell
make frontend-shell # Access frontend container shell
```

### Using Docker Compose Directly

Start services:

```bash
docker-compose up -d --build
```

View logs:

```bash
docker-compose logs -f
docker-compose logs -f backend
docker-compose logs -f frontend
```

Stop services:

```bash
docker-compose down
```

Stop and remove volumes:

```bash
docker-compose down -v
```

Rebuild specific service:

```bash
docker-compose up -d --build backend
docker-compose up -d --build frontend
```

## Architecture

```
┌─────────────────────────────────────────┐
│           Docker Bridge Network         │
│                (app-network)            │
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │   Frontend   │    │   Backend    │  │
│  │   (Nginx)    │◄───┤   (FastAPI)  │  │
│  │   Port 80    │    │   Port 8000  │  │
│  └──────────────┘    └──────────────┘  │
│         │                                │
└─────────┼────────────────────────────────┘
          │
          ▼
    [Your Browser]
```

### Network Configuration

- **app-network**: Bridge network connecting all services
- Backend exposed on port 8000
- Frontend exposed on port 80 (and 443 in production)
- Frontend proxies API requests to backend via `/api` path

### Container Details

#### Backend (FastAPI)

- **Base Image:** python:3.12-slim
- **Port:** 8000
- **Workers:** 4 (production), 1 (development)
- **Features:**
  - Tesseract OCR
  - Poppler PDF utilities
  - Health checks every 30s
  - Auto-reload in development
- **Resource Limits (Production):**
  - CPU: 2 cores
  - Memory: 2GB

#### Frontend (React + Nginx)

- **Build Stage:** node:20-alpine
- **Runtime:** nginx:alpine
- **Port:** 80
- **Features:**
  - Optimized production build
  - Gzip compression
  - API proxy to backend
  - Health checks every 30s
- **Resource Limits (Production):**
  - CPU: 1 core
  - Memory: 512MB

## Scaling

Scale backend service:

```bash
docker-compose up -d --scale backend=3
```

Note: For multiple backend instances, you'll need to add a load balancer.

## Monitoring

### Resource Usage

View real-time resource usage:

```bash
docker stats
```

### Health Status

Check container health:

```bash
docker ps
```

Or inspect specific container:

```bash
docker inspect --format='{{.State.Health.Status}}' document-processor-backend
docker inspect --format='{{.State.Health.Status}}' document-processor-frontend
```

### Service Status

```bash
docker-compose ps
```

## Troubleshooting

### Containers Won't Start

Check logs for errors:

```bash
docker-compose logs backend
docker-compose logs frontend
```

Clean restart:

```bash
docker-compose down -v
docker system prune -f
docker-compose up --build
```

### API Not Responding

Check backend health:

```bash
curl http://localhost:8000
```

Test from frontend container:

```bash
docker exec document-processor-frontend wget -qO- http://backend:8000
```

View backend logs:

```bash
docker logs document-processor-backend
```

Access backend shell:

```bash
docker exec -it document-processor-backend /bin/bash
```

### Frontend Not Loading

Check frontend logs:

```bash
docker logs document-processor-frontend
```

Test from frontend container:

```bash
docker exec document-processor-frontend wget -qO- http://localhost
```

### API Connection Issues

Ensure backend is healthy:

```bash
curl http://localhost:8000
```

Verify network connectivity:

```bash
docker network inspect app-network
```

### Permission Issues

Ensure Docker daemon is running:

```bash
docker ps
```

Add user to docker group (Linux):

```bash
sudo usermod -aG docker $USER
```

(Logout and login again)

### Port Already in Use

Check what's using the ports:

```bash
lsof -i :80
lsof -i :8000
```

Stop conflicting services or change ports in `docker-compose.yml`

### Environment Variables Not Loading

Verify `.env` file exists and has correct format:

```bash
cat .env
```

Restart containers after changing `.env`:

```bash
docker-compose down
docker-compose up -d
```

## Production Recommendations

### Security

1. **Use HTTPS**: Add SSL certificates and configure Nginx for HTTPS
2. **Environment Variables**: Never commit `.env` file to version control
3. **Secrets Management**: Use Docker secrets or external secret managers (AWS Secrets Manager, HashiCorp Vault)
4. **Run as Non-Root**: Configure containers to run as non-root users
5. **Network Isolation**: Use private networks for internal communication
6. **API Rate Limiting**: Implement rate limiting in FastAPI
7. **Input Validation**: Ensure all inputs are properly validated

### Performance

1. **Resource Limits**: Use production compose file with resource constraints
2. **Connection Pooling**: Configure database connection pools
3. **Caching**: Implement Redis for caching frequent requests
4. **CDN**: Use CDN for serving static frontend assets
5. **Load Balancing**: Add load balancer for multiple backend instances

### Reliability

1. **Logging**: Configure centralized logging (ELK Stack, CloudWatch, etc.)
2. **Monitoring**: Add Prometheus/Grafana for metrics and alerting
3. **Backup**: Implement backup strategy for uploaded documents
4. **Health Checks**: Configure proper health check endpoints
5. **Auto-Restart**: Use restart policies in production

### Maintenance

1. **Updates**: Regularly update base images and dependencies
2. **Vulnerability Scanning**: Use Docker Scout or Trivy
3. **Image Optimization**: Use multi-stage builds to reduce image size
4. **Log Rotation**: Configure log rotation to prevent disk space issues

## Cloud Deployment

### AWS ECS

1. Push images to ECR:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ECR_URL
docker-compose build
docker tag document-processor-backend:latest YOUR_ECR_URL/backend:latest
docker tag document-processor-frontend:latest YOUR_ECR_URL/frontend:latest
docker push YOUR_ECR_URL/backend:latest
docker push YOUR_ECR_URL/frontend:latest
```

2. Create ECS task definitions and services using the images

### Google Cloud Run

1. Build and push to Google Container Registry:

```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/document-processor-backend backend/
gcloud builds submit --tag gcr.io/PROJECT_ID/document-processor-frontend frontend/
```

2. Deploy services:

```bash
gcloud run deploy backend --image gcr.io/PROJECT_ID/document-processor-backend --platform managed
gcloud run deploy frontend --image gcr.io/PROJECT_ID/document-processor-frontend --platform managed
```

### Azure Container Instances

1. Build and push to Azure Container Registry:

```bash
az acr build --registry myregistry --image document-processor-backend:latest backend/
az acr build --registry myregistry --image document-processor-frontend:latest frontend/
```

2. Deploy using Container Instances:

```bash
az container create --resource-group myResourceGroup --file docker-compose.prod.yml
```

### DigitalOcean App Platform

1. Connect your repository to DigitalOcean App Platform
2. Configure build and deployment settings
3. Set environment variables in the dashboard

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Build and push
        run: |
          docker-compose build
          docker-compose push
```

### GitLab CI Example

```yaml
deploy:
  stage: deploy
  script:
    - docker-compose build
    - docker-compose -f docker-compose.prod.yml up -d
  only:
    - main
```

## Support

For issues or questions:

- Check the main [README.md](README.md)
- Review troubleshooting section above
- Check container logs for detailed error messages
- Open an issue in the repository
