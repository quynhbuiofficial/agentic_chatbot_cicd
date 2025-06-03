terraform {
  backend "s3" {
    bucket  = "qbui-chatbot-tf-state"
    region  = "us-east-1"
    key     = "s3-github-actions/terraform.tfstate"
    encrypt = true
  }
  required_version = ">= 1.2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
}