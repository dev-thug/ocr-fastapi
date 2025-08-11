variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "ap-northeast-2"
}

variable "project_name" {
  type        = string
  description = "Project name prefix"
  default     = "ocr-fastapi"
}

variable "tf_state_bucket" {
  type        = string
  description = "S3 bucket for Terraform state"
}

variable "tf_lock_table" {
  type        = string
  description = "DynamoDB table for Terraform state lock"
}

variable "vpc_cidr" {
  type        = string
  description = "VPC CIDR"
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.0.0/24", "10.0.1.0/24"]
}

variable "private_subnet_cidrs" {
  type    = list(string)
  default = ["10.0.10.0/24", "10.0.11.0/24"]
}

variable "asg_min_size" {
  type    = number
  default = 1
}

variable "asg_max_size" {
  type    = number
  default = 10
}

variable "instance_type" {
  type        = string
  description = "GPU instance type"
  default     = "g4dn.xlarge"
}

variable "ecr_image" {
  type        = string
  description = "Full ECR image URI for the application (e.g., <acct>.dkr.ecr.<region>.amazonaws.com/ocr-fastapi:latest)"
  default     = "000000000000.dkr.ecr.ap-northeast-2.amazonaws.com/ocr-fastapi:latest"
}
