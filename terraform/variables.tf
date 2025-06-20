# Terraform variables for Weather Datetime API deployment

# AWS Configuration
variable "aws_region" {
  description = "AWS region where resources will be created"
  type = string
  default = "us-east-1"
}

# Project configuration
variable "project_name" {
  description = "Name of the project"
  type = string
  default = "weather-datetime-api"
}

variable "environment" {
  description = "Environment name"
  type = string
  default = "production"
}

# ECS Configuration
variable "ecs_desired_count" {
  description = "Desired number of ECS tasks"
  type = number
  default = 2
}

variable "ecs_min_capacity" {
  description = "Minimum number of ECS tasks"
  type = number
  default = 1
}

variable "ecs_max_capacity" {
  description = "Maximum number of ECS tasks"
  type = number
  default = 10
}

# ECR Configuration
variable "ecr_repository_url" {
  description = "ECR repository URL for the Docker image"
  type = string
}

variable "image_tag" {
  description = "Docker image tag"
  type = string
  default = "latest"
}

# API Configuration
variable "openweather_api_key" {
  description = "OpenWeatherMap API key"
  type = string
  sensitive = true
}

# Network Configuration
variable "allowed_cidr_blocks" {
  description = "List of CIDR blocks allowed to access the ALB"
  type = list(string)
  default = ["0.0.0.0/0"]
}

# Logging Configuration
variable "log_retention_days" {
  description = "Number of days to retain CloudWatch logs"
  type = number
  default = 14
}

# Domain Configuration (optional)
variable "domain_name" {
  description = "Domain name for the API (e.g., api.example.com)"
  type = string
  default = null
}

variable "acm_certificate_arn" {
  description = "ACM certificate ARN for HTTPS (e.g., arn:aws:acm::.:certificate/...)"
  type = string
  default = null
}

# Resource Tags
variable "common_tags" {
  description = "Common tags to apply to all resources"
  type = map(string)
  default = {}
}