# Production Installation Guide

Copyright 2026 AI-Career-OS contributors

Licensed under the Apache License, Version 2.0.

## Production Readiness Status

AI-Career-OS `v0.13.0` is suitable for controlled private beta use. It is not yet a
broad public SaaS production platform.

Use this guide for a small private deployment where you control the users, server,
database, domain, backups, and operational access.

## 1. Production Overview

AI-Career-OS contains:

- FastAPI backend API
- React frontend dashboard
- PostgreSQL database
- Alembic database migrations
- Local JWT authentication
- User-owned candidate, application, outcome, reporting, and dashboard data

Main runtime parts:

- `backend`: FastAPI application.
- `frontend`: static React application built with Vite.
- `postgres`: PostgreSQL database.
- `migrations`: Alembic migrations run against PostgreSQL.

Authentication uses:

- email and password registration
- password hashing
- JWT access tokens
- refresh tokens
- `AUTH_SECRET` for token signing

Do not deploy with demo secrets.

## 2. Server Prerequisites

You need:

- Linux server, for example Ubuntu 22.04 or 24.04.
- Docker.
- Docker Compose plugin.
- Git.
- A domain name or local IP address.
- Reverse proxy, optional but recommended.
- HTTPS, strongly recommended.

Check Docker:

```bash
docker --version
docker compose version
```

Check Git:

```bash
git --version
```

Recommended server ports:

- `80` and `443` for public web traffic through Nginx or another reverse proxy.
- Backend exposed internally or on `8000` only when needed.
- PostgreSQL should not be exposed publicly.

## 3. Environment Setup

Clone de repo:

```bash
cd ~
git clone https://github.com/gooskoen/AI-Career-OS.git
cd AI-Career-OS
```

Controle:

```bash
git describe --tags
```

Ik verwacht:

```bash
v0.13.0
```

Create a production environment file:

```bash
cp .env.example .env.production
```

Required variables:

```env
POSTGRES_DB=ai_career_os
POSTGRES_USER=ai_career_os
POSTGRES_PASSWORD=replace-with-a-strong-database-password
DATABASE_URL=postgresql://ai_career_os:replace-with-a-strong-database-password@postgres:5432/ai_career_os
AUTH_SECRET=replace-with-a-strong-auth-secret
FRONTEND_API_BASE_URL=https://your-domain.example.com
```

### Generate A Strong AUTH_SECRET

Use one of these commands:

```bash
openssl rand -hex 32
```

or:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Put the generated value in `AUTH_SECRET`.

Important:

- Use a unique value per environment.
- Do not commit `.env.production`.
- Do not reuse demo secrets.
- If `AUTH_SECRET` changes, existing tokens become invalid.

## 4. Docker Compose Production Setup

This repository includes `docker-compose.prod.yml` as a documented production-style
example.

Start from it, review every value, and adjust domains, ports, and volume paths for
your server.

Expected services:

- `postgres`
- `backend`
- `migrations`
- `frontend`

Expected production characteristics:

- named PostgreSQL volume
- restart policies
- healthchecks
- internal Docker network
- frontend public port
- backend API port bound to localhost by default
- one-shot migration runner with Alembic files mounted from the repository

The example binds the backend to `127.0.0.1:8000:8000`. This is intentional for
reverse proxy deployments. If you change it to `8000:8000`, firewall port `8000`
so the backend is not exposed directly to the public internet.

The `migrations` service is placed behind the `tools` profile, so it does not run
as a long-lived service during normal `up`. It runs only when you explicitly call
the documented migration command.

Build and start:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

Check running containers:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml ps
```

Stop:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml down
```

## 5. Database Setup

PostgreSQL is created by the `postgres` container using:

- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`

The backend uses:

- `DATABASE_URL`

Run migrations after containers are up:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic upgrade head
```

Verify migration head:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic heads
```

The output should show the latest migration head.

The production compose file uses a one-shot `migrations` service. It builds from
the backend image and mounts `alembic.ini` plus the `migrations/` directory into
the container, so the documented Alembic command has access to the migration
configuration and scripts.

Before every production migration:

1. Take a PostgreSQL backup.
2. Confirm the backup file exists and is non-empty.
3. Run `alembic upgrade head`.
4. Run the smoke test checklist.

Rollback warning:

- Alembic downgrade is not assumed safe for production.
- Take a backup before every migration.
- If a migration fails after changing data, restoring from backup may be required.

If migrations fail:

1. Check `DATABASE_URL`.
2. Check PostgreSQL container health.
3. Check migration runner logs.
4. Do not delete the database volume unless you intentionally want to remove all data.

## 6. Backend Deployment

Build and start backend:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build backend
```

View logs:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml logs -f backend
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

Common backend errors:

- Missing `AUTH_SECRET`: set `AUTH_SECRET` in `.env.production`.
- Database connection failed: check `DATABASE_URL` and PostgreSQL health.
- Migration missing: run the documented `migrations` service command.
- Port conflict: change host port mapping or stop the process using the port.
- Backend reachable publicly on `8000`: bind to `127.0.0.1:8000:8000` or firewall it.

## 7. Frontend Deployment

The frontend is a static React app built with Vite.

The provided compose file serves it with `vite preview`. That is suitable for a
controlled private beta or simple single-server validation, but it is not the
recommended hardened production static server. For broader production use, build
the frontend once and serve `frontend/dist` with Nginx, Caddy, or a managed static
hosting service.

Build through Docker Compose:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build frontend
```

The frontend build needs an API base URL. Set:

```env
FRONTEND_API_BASE_URL=https://your-domain.example.com
```

For local IP testing:

```env
FRONTEND_API_BASE_URL=http://your-server-ip:8000
```

Verify:

1. Open the frontend URL in a browser.
2. Confirm the login page appears.
3. Register a test user.
4. Log in.
5. Confirm the dashboard loads.

## 8. First User Setup

After the app is running:

1. Open the frontend URL.
2. Click `Register`.
3. Enter email, display name, and password.
4. Log in.
5. Create a candidate through the beta workflow panel.
6. Import a job through the beta workflow panel.
7. Review or generate a match.
8. Generate an application package.
9. Create an application.
10. Move the application through the pipeline.
11. Record an outcome.
12. Open Insights.
13. Verify dashboard and reporting values update.

If any step fails, check:

- browser developer console
- frontend container logs
- backend container logs
- backend `/health`
- database migration status

## 9. Reverse Proxy And HTTPS

HTTPS is strongly recommended. Use Nginx, Caddy, Traefik, or a cloud load balancer.

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /auth/ {
        proxy_pass http://127.0.0.1:8000/auth/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /applications/ {
        proxy_pass http://127.0.0.1:8000/applications/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /reporting/ {
        proxy_pass http://127.0.0.1:8000/reporting/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /candidates {
        proxy_pass http://127.0.0.1:8000/candidates;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /jobs/ {
        proxy_pass http://127.0.0.1:8000/jobs/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /matches/ {
        proxy_pass http://127.0.0.1:8000/matches/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /outcomes {
        proxy_pass http://127.0.0.1:8000/outcomes;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Add HTTPS with Certbot or your preferred TLS provider.

After HTTPS is enabled, set:

```env
FRONTEND_API_BASE_URL=https://your-domain.example.com
```

## 10. Backup And Restore

The most important data lives in PostgreSQL.

Back up PostgreSQL:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T postgres \
  sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > ai-career-os-backup.sql
```

Verify the backup file:

```bash
ls -lh ai-career-os-backup.sql
```

Do not continue with an upgrade or restore if the backup file is missing or
empty.

Restore PostgreSQL:

1. Take an emergency backup of the current database before overwriting it:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T postgres \
  sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > ai-career-os-before-restore.sql
```

2. Restore the selected backup:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T postgres \
  sh -c 'psql -U "$POSTGRES_USER" "$POSTGRES_DB"' < ai-career-os-backup.sql
```

3. Run migrations in case the restored dump is behind the current application:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic upgrade head
```

4. Restart application services:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml restart backend frontend
```

5. Run the restore smoke test:

- Log in with a known user.
- Confirm the dashboard loads.
- Confirm the application list or Kanban board loads.

Also back up:

- `.env.production`
- deployment notes
- reverse proxy configuration
- database dumps

Do not rely only on Docker volumes as backups.

## 11. Upgrade Procedure

1. SSH into the server.
2. Go to the repository directory.
3. Fetch latest code:

```bash
git fetch origin
git checkout main
git pull --ff-only origin main
```

4. Back up PostgreSQL:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T postgres \
  sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > ai-career-os-before-upgrade.sql
```

5. Rebuild containers:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

6. Run migrations:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic upgrade head
```

7. Restart services:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml restart
```

8. Run smoke tests.

Rollback warning:

- Do not assume `alembic downgrade` is safe.
- If an upgrade fails after applying migrations, restore from
  `ai-career-os-before-upgrade.sql` or another verified backup.
- Keep the backup until the upgraded system has passed smoke testing.

## 12. Smoke Test Checklist

After install or upgrade, verify:

- [ ] Backend health works.
- [ ] Frontend loads.
- [ ] Register works.
- [ ] Login works.
- [ ] Dashboard loads.
- [ ] Create candidate works.
- [ ] Import job works.
- [ ] Create application works.
- [ ] Kanban board loads.
- [ ] Application transition works.
- [ ] Outcome recording works.
- [ ] Reporting loads.
- [ ] Logout works.

## 13. Troubleshooting

### Missing AUTH_SECRET

Symptom:

- Backend exits on startup.

Fix:

- Set `AUTH_SECRET` in `.env.production`.
- Use a strong generated value.
- Restart backend.

### Database Connection Failed

Symptom:

- Backend logs show connection errors.

Fix:

- Check `DATABASE_URL`.
- Check PostgreSQL container status.
- Confirm username, password, host, port, and database name.

### Migrations Failed

Symptom:

- `alembic upgrade head` fails.

Fix:

- Confirm database is reachable.
- Use the `migrations` service from `docker-compose.prod.yml`.
- Confirm `alembic.ini` and `migrations/` exist in the repository directory.
- Check current migration state:

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml run --rm migrations alembic current
```

- Review migration logs.
- Back up before manual fixes.

### Frontend Cannot Reach Backend

Symptom:

- Login fails.
- Browser console shows failed API requests.

Fix:

- Check `FRONTEND_API_BASE_URL`.
- Check reverse proxy rules.
- Confirm backend `/health` works.
- Confirm frontend was rebuilt after changing API base URL.

### CORS Or API URL Issue

Symptom:

- Browser blocks requests.

Fix:

- Prefer same-origin reverse proxy routing.
- If using separate domains, configure backend CORS in a future hardening step.
- Make sure frontend points at the public API URL users can reach.

### Login Fails

Symptom:

- Register works but login fails.

Fix:

- Check password.
- Check backend logs.
- Confirm `AUTH_SECRET` did not change between token creation and use.
- Clear browser session storage and try again.

### Token Expired

Symptom:

- User is logged out or API requests fail with `401`.

Fix:

- Refresh token should retry automatically in the frontend.
- If it still fails, log out and log in again.
- Check whether `AUTH_SECRET` changed.

### Port Already In Use

Symptom:

- Docker cannot bind `3000`, `8000`, or `5432`.

Fix:

- Stop the process using the port.
- Or change the host port mapping in `docker-compose.prod.yml`.

## 14. Security Warnings

Production safety checklist:

- Do not use demo secrets.
- Use HTTPS.
- Protect the database.
- Do not expose PostgreSQL publicly.
- Do not expose the backend directly when using a reverse proxy; bind it to
  `127.0.0.1` or firewall port `8000`.
- Back up regularly.
- Store `.env.production` securely.
- Restrict server SSH access.
- Keep Docker and the OS patched.
- Review npm audit findings before broad rollout.
- Refresh token storage is MVP-level in `v0.13.0`.
- Additional production hardening is still recommended before public SaaS launch.

Recommended future hardening:

- HttpOnly cookie or backend-for-frontend session model.
- CORS allowlist.
- Rate limiting.
- Password reset.
- Token revocation/logout server-side.
- Monitoring and alerting.
- Automated backups.
- Separate production/staging environments.
