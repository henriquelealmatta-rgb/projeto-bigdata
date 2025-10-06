# Backend configuration for Terraform state
# Uncomment and configure after creating the state bucket

# terraform {
#   backend "s3" {
#     bucket         = "movies-pipeline-terraform-state"
#     key            = "aws/terraform.tfstate"
#     region         = "us-east-1"
#     encrypt        = true
#     dynamodb_table = "movies-pipeline-terraform-locks"
#   }
# }

