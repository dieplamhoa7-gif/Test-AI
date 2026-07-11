param(
  [Parameter(Mandatory=$true)] [string] $ProjectId,
  [string] $Region = "asia-southeast1",
  [string] $Service = "hoa-investment-model3"
)

$ErrorActionPreference = "Stop"

Write-Host "Deploying $Service to Cloud Run project=$ProjectId region=$Region"
Write-Host "Safety: min instances=0, max instances=2, no API keys are read from files or committed."

gcloud config set project $ProjectId

gcloud run deploy $Service `
  --source . `
  --region $Region `
  --allow-unauthenticated `
  --min-instances 0 `
  --max-instances 2 `
  --concurrency 4 `
  --cpu 1 `
  --memory 1Gi `
  --timeout 900 `
  --set-env-vars REQUEST_TIMEOUT=15,MAX_ARTICLES_PER_SOURCE=8,SUMMARY_MAX_WORDS=50

Write-Host "Done. Set AI secrets in Cloud Run env/secrets after deploy if needed; do not put keys in frontend."
