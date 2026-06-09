# PLANIFICATOR-3000 Deployment Checklist

## Railway

- [ ] Single Railway project created
- [ ] Service `api` created
- [ ] Service `web` created
- [ ] API Dockerfile path: `apps/api/Dockerfile`
- [ ] Web Dockerfile path: `apps/web/Dockerfile`
- [ ] API health check path: `/api/health`
- [ ] Web health check path: `/`

## API environment

- [ ] `APP_ENV=production`
- [ ] `API_PREFIX=/api`
- [ ] `CORS_ORIGINS=https://your-web-service.up.railway.app`
- [ ] `GOOGLE_SHEET_ID` configured
- [ ] `GOOGLE_SERVICE_ACCOUNT_JSON` configured
- [ ] `GOOGLE_WORKSHEET_MONTHLY_PLAN=Monthly Plan`
- [ ] `GOOGLE_WORKSHEET_COMPLETED_TASKS=Completed Tasks`
- [ ] `GOOGLE_WORKSHEET_RECURRING_TASKS=Recurring Tasks`
- [ ] `GOOGLE_WORKSHEET_TEAM_ROSTER=Team Roster`
- [ ] `GOOGLE_WORKSHEET_CONFIG=Configuration`

## Web environment

- [ ] `NEXT_PUBLIC_API_URL=https://your-api-service.up.railway.app`
- [ ] `NEXT_PUBLIC_APP_URL=https://your-web-service.up.railway.app`

## Google Sheets

- [ ] Google Sheet exists
- [ ] Service account has access
- [ ] Required worksheets exist
- [ ] Demo data is present

## Smoke tests

- [ ] `/api/health` returns `status: ok`
- [ ] `/api/smoke` returns `status: ok`
- [ ] Dashboard opens
- [ ] Dashboard can reach API
- [ ] No browser CORS errors
