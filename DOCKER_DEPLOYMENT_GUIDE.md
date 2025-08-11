# Docker Deployment Guide for Smart Dispute Canada

## Prerequisites

1. Docker installed on your system
2. Docker Compose installed (optional but recommended)
3. Git installed on your system

## Deployment Options

### Option 1: Using Docker Compose (Recommended)

This option includes both the application and PostgreSQL database in a single deployment.

#### Steps

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd smart-dispute-flask-app
   ```

2. Build and start the services:

   ```bash
   docker-compose up -d
   ```

3. The application will be available at <https://localhost:8080>

4. To stop the services:

   ```bash
   docker-compose down
   ```

### Option 2: Using Individual Docker Commands

#### Steps for Individual Docker Commands

1. Build the Docker image:

   ```bash
   docker build -t smart-dispute-canada .
   ```

2. Run PostgreSQL container:

   ```bash
   docker run -d \
     --name postgres-db \
     -e POSTGRES_DB=smartdispute_db \
     -e POSTGRES_USER=smartdispute_user \
     -e POSTGRES_PASSWORD=smartdispute_password \
     -v postgres_data:/var/lib/postgresql/data \
     -p 5432:5432 \
     postgres:13
   ```

3. Run the application container:

   ```bash
   docker run -d \
     --name smart-dispute-app \
     -p 8080:8080 \
     -e FLASK_ENV=production \
     -e SECRET_KEY=your-secure-key-here \
     -e DATABASE_URL=postgresql://smartdispute_user:smartdispute_password@postgres-db:5432/smartdispute_db \
     -e OPENAI_API_KEY=your-openai-api-key \
     -e ANTHROPIC_API_KEY=your-anthropic-api-key \
     -v $(pwd)/config/certificates:/app/config/certificates \
     -v $(pwd)/uploads:/app/uploads \
     --link postgres-db \
     smart-dispute-canada
   ```

## Environment Variables

The following environment variables can be configured:

| Variable | Description | Default/Example |
|----------|-------------|-----------------|
| `FLASK_ENV` | Environment mode | `production` |
| `SECRET_KEY` | Flask secret key | Generate a secure random string |
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://user:pass@host:5432/db` |
| `OPENAI_API_KEY` | OpenAI API key | Your OpenAI API key |
| `ANTHROPIC_API_KEY` | Anthropic API key | Your Anthropic API key |
| `SSL_CERT_PATH` | SSL certificate path | `/app/config/certificates/cert.pem` |
| `SSL_KEY_PATH` | SSL private key path | `/app/config/certificates/key.pem` |

## SSL Configuration

SSL certificates should be placed in the `config/certificates/` directory:
- `smartdispute-canada.me.pem` (certificate)
- `smartdispute-canada.me.key` (private key)

## Data Persistence

Data is persisted using Docker volumes:
- PostgreSQL data is stored in a named volume `postgres_data`
- Uploaded files are stored in the `uploads/` directory

## Health Checks

The application includes health checks that verify:
- Database connectivity
- File system access
- Memory usage
- CPU usage
- Disk space
- SSL certificate validity

## Monitoring

View logs with:

```bash
docker-compose logs -f
```

Or for individual containers:

```bash
docker logs -f smart-dispute-app
docker logs -f postgres-db
```

## Scaling

To scale the application:

```bash
docker-compose up -d --scale web=3
```

## Backup and Restore

### Database Backup

```bash
docker exec postgres-db pg_dump -U smartdispute_user smartdispute_db > backup.sql
```

### Database Restore

```bash
docker exec -i postgres-db psql -U smartdispute_user smartdispute_db < backup.sql
```

## Troubleshooting

### Common Issues

1. **Database connection errors**: Ensure PostgreSQL is running and connection details are correct
2. **SSL certificate issues**: Verify certificate files exist and have correct permissions
3. **Port conflicts**: Change the port mapping in docker-compose.yml
4. **Permission errors**: Check file permissions for certificates and uploads directory

### Checking Container Status

```bash
docker-compose ps
```

### Accessing Container Shell

```bash
docker-compose exec web bash
docker-compose exec db bash
```

## Updating the Application

1. Pull the latest code:

   ```bash
   git pull
   ```

2. Rebuild and restart:

   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## Security Considerations

- Never commit secrets to version control
- Use strong, randomly generated secret keys
- Regularly update base Docker images
- Restrict access to the database port (5432) from external networks
- Use HTTPS in production environments