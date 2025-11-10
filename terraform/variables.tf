variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
}

variable "zones" {
  description = "GCP zones for multi-zone deployment"
  type        = list(string)
}

variable "network_name" {
  description = "Name of the VPC network"
  type        = string
}

variable "subnet_name" {
  description = "Name of the subnet"
  type        = string
}

variable "subnet_cidr" {
  description = "CIDR range for the subnet"
  type        = string
}

variable "pods_cidr_name" {
  description = "Name for pods secondary CIDR range"
  type        = string
}

variable "pods_cidr" {
  description = "Secondary CIDR range for pods"
  type        = string
}

variable "services_cidr_name" {
  description = "Name for services secondary CIDR range"
  type        = string
}

variable "services_cidr" {
  description = "Secondary CIDR range for services"
  type        = string
}

variable "cluster_name" {
  description = "Name of the GKE cluster"
  type        = string
}

variable "node_count_per_zone" {
  description = "Number of nodes per zone"
  type        = number
}

variable "node_machine_type" {
  description = "Machine type for GKE nodes"
  type        = string
}

variable "node_disk_size_gb" {
  description = "Disk size for each node in GB"
  type        = number
}

variable "min_node_count" {
  description = "Minimum nodes per zone for autoscaling"
  type        = number
}

variable "max_node_count" {
  description = "Maximum nodes per zone for autoscaling"
  type        = number
}

variable "artifact_registry_repository" {
  description = "Artifact Registry repository name"
  type        = string
}

variable "labels" {
  description = "Labels to apply to all resources"
  type        = map(string)
}