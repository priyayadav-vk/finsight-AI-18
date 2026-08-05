FinSight AI — Deployment guide (Docker + docker-compose) 

This document explains how to deploy the app to a Linux VPS using Docker and docker-compose, with an example systemd unit and an Nginx reverse proxy + Certbot for TLS.

Prerequisites on VPS
- Ubuntu 22.04 / Debian 12 or similar
- Docker Engine installed (https://docs.docker.com/engine/install/)
- docker-compose (v2+ or standalone) installed
- A non-root account with sudo privileges
- A domain name pointed to the server (for HTTPS)

Files added to repository
- backend/Dockerfile
- backend/docker-compose.yml
- backend/deploy_run.sh (helper to build/run)
- backend/start.sh
- systemd/finsightai.service.template (template unit file)
- nginx/finsightai.conf.template (nginx reverse-proxy template)

Quick start (recommended)
1. Copy project to VPS
   scp -r /local/path/to/finsightai user@your-vps:/home/user/

2. On VPS: go to project folder
   cd /home/user/finsightai
   sudo chown -R $USER:$USER .

3. Build and run with docker-compose
   cd backend
   # Make script executable once
   chmod +x deploy_run.sh
   ./deploy_run.sh up

4. Check containers and logs
   docker ps
   ./deploy_run.sh logs

5. (Optional) Enable as systemd service
   # Edit template and replace /home/<user>/finsightai with your path
   sudo cp systemd/finsightai.service.template /etc/systemd/system/finsightai.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now finsightai.service
   sudo systemctl status finsightai.service

Nginx reverse-proxy + TLS (Certbot)
1. Install Nginx and Certbot
   sudo apt update && sudo apt install -y nginx certbot python3-certbot-nginx

2. Copy nginx config, adjust server_name
   sudo cp nginx/finsightai.conf.template /etc/nginx/sites-available/finsightai
   sudo sed -i 's/example.com/your.domain.tld/g' /etc/nginx/sites-available/finsightai
   sudo ln -s /etc/nginx/sites-available/finsightai /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx

3. Obtain certificate
   sudo certbot --nginx -d your.domain.tld

4. Adjust firewall to allow 80/443
   sudo ufw allow 'Nginx Full'

Notes & hardening
- Expose only localhost:8501; use Nginx to serve the app publicly.
- Store persistent app data under ./data (mounted into container). This ensures live caches and company lists persist across container restarts.
- Consider adding automatic backups for ./data and any saved models.
- Monitor logs and container health; docker-compose includes a healthcheck for the Streamlit root path.

Troubleshooting
- If Streamlit fails due to starlette/streamlit import mismatch: ensure requirements.txt pins compatible Streamlit version (the provided file uses streamlit==1.28.1). If your environment needs a different Streamlit version, update requirements.txt and rebuild the image.
- If the app is slow to start due to model training on first-run, consider pre-training models offline and adding them to ./data/models, or increase VM CPU/memory.
- For Streamlit Cloud deployments, set `STREAMLIT_CLOUD=1` to enable a safe demo fallback when no local models are present, and set `MODEL_BASE_URL` to a public URL where model artifacts can be downloaded.

Advanced
- Add a small service (e.g., gunicorn + uvicorn) as a lightweight HTTP health endpoint if you prefer not to rely on Streamlit's root path.
- Use Docker image registry (Docker Hub, GitHub Packages) and deploy by pulling images instead of building on VPS.

If you'd like, I can now:
- Build a production Docker image locally and run it here for smoke testing (note: we cannot start long-lived servers in this session without detach), or
- Customize the Dockerfile to include a small /health endpoint and a multi-stage build to shrink image size.

Which follow-up would you like? (reply with one):
- "Smoke test image locally"
- "Add health endpoint and multi-stage shrink"
- "No, I'm done — give me the checklist only"
