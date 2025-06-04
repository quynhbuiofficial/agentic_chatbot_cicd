variable "keypair_public" {
  type = string
}
variable "ec2_frontend_name" {
  type    = string
  default = "chatbot-frontend"
}

variable "ec2_backend_name" {
  type    = string
  default = "chatbot-backend"
}

variable "ec2_services_name" {
  type = list(string)
  default = ["chatbot-elasticsearch", "chatbot-mcp-server",
  "chatbot-neo4j"]
}

variable "ec2_types" {
  type    = list(string)
  default = ["t2.medium", "t2.small", "t2.micro"]
}

variable "ec2_storages" {
  type    = list(number)
  default = [13, 13, 8]
}

variable "aws_region" {
  default = "us-east-1"
}

variable "enviroment" {
  default = "qbui-chatbot"
}

variable "vpc_cidr" {
  default     = "10.0.0.0/16"
  description = "CIDR block of the vpc"
}

variable "public_subnets_cidr" {
  type    = list(string)
  default = ["10.0.0.0/22", "10.0.4.0/22"]
}

variable "private_subnet_cidr" {
  type        = string
  default     = "10.0.8.0/22"
  description = "CIDR block for Private Subnet"
}


















