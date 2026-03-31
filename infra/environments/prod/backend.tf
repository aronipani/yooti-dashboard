terraform {
  backend "s3" {
    bucket         = "yooti-dashboard-terraform-state-prod"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "yooti-dashboard-terraform-locks"
    encrypt        = true
  }
}
