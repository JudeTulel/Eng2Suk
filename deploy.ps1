# Deploy to Google Cloud Run

# 1. Set Project ID
$PROJECT_ID = "auth-4eef8"
$IMAGE_NAME = "pokot-translator"
$REGION = "us-central1"

Write-Host "Deploying to Project: $PROJECT_ID"

# 2. Build Container Image
Write-Host "Building container image..."
gcloud builds submit --tag "gcr.io/$PROJECT_ID/$IMAGE_NAME" .

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed."
    exit 1
}

# 2.5 Get Hugging Face Token
if (-not $env:HF_TOKEN) {
    $HF_TOKEN = Read-Host "Please enter your Hugging Face API Token (to avoid rate limits)"
} else {
    $HF_TOKEN = $env:HF_TOKEN
}

if (-not $HF_TOKEN) {
    Write-Warning "No Hugging Face Token provided. Rate limits may occur."
}

# 3. Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..."
$deployArgs = @(
    "run", "deploy", $IMAGE_NAME,
    "--image", "gcr.io/$PROJECT_ID/$IMAGE_NAME",
    "--region", $REGION,
    "--platform", "managed",
    "--allow-unauthenticated",
    "--memory", "2Gi",
    "--cpu", "1"
)

if ($HF_TOKEN) {
    $deployArgs += "--set-env-vars", "HF_TOKEN=$HF_TOKEN"
}

gcloud @deployArgs

if ($LASTEXITCODE -ne 0) {
    Write-Error "Deployment failed."
    exit 1
}

Write-Host "Deployment Complete!"
