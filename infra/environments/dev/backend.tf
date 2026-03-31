terraform {
  backend "s3" {
    bucket         = "yooti-dashboard-terraform-state-dev"
    key            = "dev/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "yooti-dashboard-terraform-locks"
    encrypt        = true
  }
}
