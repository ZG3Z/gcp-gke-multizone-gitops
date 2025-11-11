resource "google_cloudbuild_trigger" "main_branch" {
  name     = "deploy-on-push-main"
  location = var.region

  github {
    owner = var.github_owner
    name  = var.github_repo
    push {
      branch = "^main$"
    }
  }

  filename = "cloudbuild.yaml"

  service_account = google_service_account.cloud_build.id

  depends_on = [
    google_project_service.required_apis,
    google_service_account.cloud_build,
  ]
}