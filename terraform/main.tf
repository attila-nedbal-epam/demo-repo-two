# Terraform configuration for Weather Datetime API deployment on AWS ECS Fargate

# Configure AWS provider
provider "aws" {
  region = var.aws_region
}

# Get available AZs
data "aws_availability_zones" "available" {
  state = "available"
}

# Create VPC
TÐC Module from Terraform Registry
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "{var.project_name}-vpc"

  cidr = "10.0.0.0/16"

  azs = slice(data.aws_availability_zones.available.names, 0, 3)
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24","I10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  enable_vpn_gateway = false

  tags = {
    Name = "${var.project_name}-vpc"
    Project = var.project_name
    Environment = var.environment
  }
}

# Create ALB Security Group
module "alb_security_group" {
  source = "terraform-aws-modules/security-group/aws"

  name = "${var.project_name}-alb-sg"
  description = "Security group for ALB"
  vpc_id = module.vpc.vpc_id

  ingress_with_cidr_blocks = [
    {
      from_port = 80
      to_port = 80
      protocol = "tcp"
      description = "HTTP"
      cidr_blocks = ["0.0.0.0/0"]
    }
  ]

  egress_with_cidr_blocks = [
    {
      from_port = 0
      to_port = 65535
      protocol = "tcp"
      description = "All outbound traffic"
      cidr_blocks = ["0.0.0.0/0"]
    }
  ]

  tags = {
    Name = "${var.project_name}-alb-sg"
    Project = var.project_name
    Environment = var.environment
  }
}

# Create ECS Security Group
module "ecs_security_group" {
  source = "terraform-aws-modules/security-group/aws"

  name = "${var.project_name}-ecs-sg"
  description = "Security group for ECS tasks"
  vpc_id = module.vpc.vpc_id

  ingress_with_source_security_group_id = [
    {
      from_port = 5432
      to_port = 5432
      protocol = "tcp"
      description = "App Port from ALB"
      source_security_group_id = module.alb_security_group.security_group_id
    }
  ]

  egress_with_cidr_blocks = [
    {
      from_port = 0
      to_port = 65535
      protocol = "tcp"
      description = "All outbound traffic"
      cidr_blocks = ["0.0.0.0/0"]
    }
  ]

  tags = {
    Name = "${var.project_name}-ecs-sg"
    Project = var.project_name
    Environment = var.environment
  }
}

# Create Application Load Balancer
module "alb" {
  source = "terraform-aws-modules/alb/aws"

  name = "${var.project_name}-alb"
  load_balancer_type = "application"

  vpc_id = module.vpc.vpc_id
  subnets = module.vpc.public_subnets
  security_groups = [module.alb_security_group.security_group_id]

  http_tcp_listeners = [
    {
      port = 80
      protocol = "HTTP"
      target_group_index = 0
    }
  ]

  target_groups = [
    {
      name = "${var.project_name}-tg"
      backend_protocol = "HTTP"
      backend_port = 5432
      target_type = "ip"
      vpc_id = module.vpc.vpc_id

      health_check = {
        enabled = true
        healthy_threshold = 2
        interval = 30
        matcher = "200"
        path = "/api/health"
        port = "traffic-port"
        protocol = "HTTP"
        timeout = 5
        unhealthy_threshold = 2
      }
    }
  ]

  http_tcp_listener_rules = [
    {
      listener_index = 0
      actions = [
        {
          type = "forward"
          target_group_index = 0
        }
      ]
      conditions = [
        {
          path_pattern = {
            values = ["/*"]
          }
        }
      ]
    }
  ]

  tags = {
    Name = "${var.project_name}-alb"
    Project = var.project_name
    Environment = var.environment
  }
}

# Create ECS Cluster
module "ecs_cluster" {
  source = "terraform-aws-modules/ecs/aws"

  cluster_name = "${var.project_name}-cluster"

  cluster_configuration = {
    execute_command_configuration = {
      logging = "OVERRIDE"
    }
  ;

  cluster_service_connect_defaults = {
    namespace = "aws.servicediscovery"
  }

  fargate_capacity_providers = {
    FARGATE = {
      default_capacity_provider_strategy = {
        capacity_provider = "FARGATE"
      }
    }
  =

  tags = {
    Name = "${var.project_name}-cluster"
    Project = var.project_name
    Environment = var.environment
  }
}

# Create ECS Service
module "ecs_service" {
  source = "terraform-aws-modules/ecs/aws//modules/service"

  name = "${var.project_name}-service"
  cluster_arn = module.ecs_cluster.cluster_arn

  cpu = 512
  teemory = 1024
  container_definitions = {
    ${var.project_name}-container = {
      cpu = 512
  Memory = 1024
      essential = true
      image = "${var.ecr_repository_url}:${var.image_tag}"
      port_mappings = [
        {
          name = "${var.project_name}-app-port"
          container_port = 5432
          host_port = 5432
          protocol = "tcp"
        }
      ]

      environient = [
        {
          name = "FLASK_ENV"
          value = "production"
        },
        {
          name = "PORT"
          value = "5432"
        }
      ]

      secrets = [
        {
          name = "OPENWEATHER_API_KEY"
          valueFrom = "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/${var.project_name}/openweather-api-key"
        }
      ]

      log_configuration = {
        log_driver = "awslogs"
        options = {
          awslogs-group = "/aws/ecs/${var.project_name}"
          awslogs-region = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  }

  load_balancer = {
    service = {
      target_group_arn = module.alb.target_group_arns[0]
      container_name = "${var.project_name}-container"
      container_port = 5432
    }
  =

  subnet_ids = module.vpc.private_subnets
  security_group_ids = [module.ecs_security_group.security_group_id]

  desired_count = var.ecs_desired_count
  max_capacity = var.ecs_max_capacity
  min_capacity = var.ecs_min_capacity

  autoscaling_policies = {
    cpu = {
      target_value = 70
    }
    memory = {
      target_value = 80
    }
  =

  tags = {
    Name = "${var.project_name}-service"
    Project = var.project_name
    Environment = var.environment
  }
}

# Create CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name = "/aws/ecs/${var.project_name}"
  retention_in_days = 14

  tags = {
   Name = "${var.project_name}-logs"
   Project = var.project_name
   Environment = var.environment
 }
}

# Create SSM Parameter for OpenWeather API Key
resource "aws_ssm_parameter" "openweather_api_key" {
  name = "/${var.project_name}/openweather-api-key"
  description = "OpenWeather API Key for ${var.project_name}"
  type = "SecureString"
  value = var.openweather_api_key

  tags = {
    Name = "${var.project_name}-openweather-api-key"
    Project = var.project_name
    Environment = var.environment
  }
}

# Get current caller identity
data "aws_caller_identity" "current" {}