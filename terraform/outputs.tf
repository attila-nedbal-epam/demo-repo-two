# Terraform outputs for Weather Datetime API deployment

# VPC Outputs
output "vpc_id" {
  description = "ID of the VPC"
  value = module.vpc.vpc_id
}

output "public_subnets" {
  description = "List of IDs of the public subnets"
  value = module.vpc.public_subnets
}

output "private_subnets" {
  description = "List of IDs of the private subnets"
  value = module.vpc.private_subnets
}

# ALB Outputs
output "alb_dns" {
  description = "DNS name of the Application Load Balancer"
  value = module.alb.lb_dns_name
}

output "alb_zone_id" {
  description = "Zone ID of the Application Load Balancer"
  value = module.alb.lb_zone_id
}

output "alb_arn" {
  description = "ARN of the Application Load Balancer"
  value = module.alb.lb_arn
}

output "alb_url" {
  description = "URL of the Application Load Balancer (including protocol)"
  value = "http://${module.alb.lb_dns_name}"
}

# ECS Outputs
output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value = module.ecs_cluster.cluster_name
}

output "ecs_cluster_arn" {
  description = "ARN of the ECS cluster"
  value = module.ecs_cluster.cluster_arn
}

output "ecs_service_name" {
  description = "Name of the ECS service"
  value = module.ecs_service.service_name
}

output "ecs_service_arn" {
  description = "ARN of the ECS service"
  value = module.ecs_service.service_arn
}

# Security Groups Outputs
output "alb_security_group_id" {
  description = "ID of the ALB security group"
  value = module.alb_security_group.security_group_id
}

output "ecs_security_group_id" {
  description = "ID of the ECS security group"
  value = module.ecs_security_group.security_group_id
}

# CloudWatch Outputs
output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value = aws_cloudwatch_log_group.app.name
}

# SSM Parameter Outputs
output "ssm_parameter_arn" {
  description = "ARN of the SSM parameter for OpenWeather API key"
  value = aws_ssm_parameter.openweather_api_key.arn
}

# API Endpoints Outputs
output "api_endpoints" {
  description = "API endpoints available"
  value = {
    base_url = "http://${module.alb.lb_dns_name}"
    datetime = "http://${module.alb.lb_dns_name}/api/datetime"
    weather = "http://${module.alb.lb_dns_name}/api/weather"
    combined = "http://${module.alb.lb_dns_name}/api/combined"
    health = "http://${module.alb.lb_dns_name}/api/health"
  }
}

# Monitoring Information
output "monitoring" {
  description = "Monitoring information"
  value = {
    cloudwatch_logs = "https://console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#logStream:logGroup=%2Faws%2Fecs%2F${var.project_name}"
    ecs_service = "https://console.aws.amazon.com/ecs/home?region=${var.aws_region}#clusters/${module.ecs_cluster.cluster_name}/services/${module.ecs_service.service_name}/details"
    alb_metrics = "https://console.aws.amazon.com/ec2/home?region=${var.aws_region}#LoadBalancers:sort=loadBalancerName;search=${module.alb.lb_id}"
  }
}

# Deployment Information
output "deployment_info" {
  description = "Deployment information"
  value = {
    region = var.aws_region
    environment = var.environment
    project = var.project_name
    ecr_repository = var.ecr_repository_url
    image_tag = var.image_tag
  }
}