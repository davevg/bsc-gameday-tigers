variable "region" {
  type        = string
  description = "AWS region"
}

variable "project" {
  type        = string
  description = "Project name"
}

variable "account_id" {
  type        = string
  description = "AWS account ID"
}

variable "eks_oidc_provider" {
  type        = string
  description = "OIDC provider URL for EKS"
}

variable "namespace" {
  type        = string
  description = "Kubernetes namespace"
}

variable "domain" {
  description = "Domain"
  type        = string
}

variable "service_account_name" {
  description = "Service account name"
  type        = string
}
variable "sagemaker_endpoint_name" {
  description = "Sagemaker endpoint name"
  type        = string
}

variable "model_metadata_file" {
  description = "Model metadata file"
  type        = string
  
}
variable "alert_email" {
  description = "Email address for alerts"
  type        = string
  default = ""
}