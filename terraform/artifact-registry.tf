resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region
  repository_id = var.artifact_registry_repository
  description   = "Docker repository for application images"
  format        = "DOCKER"

  labels = var.labels

  depends_on = [
    google_project_service.required_apis,
  ]
}
