/*
This file is required.
It configures the S3 remote state backend for this environment.
The scope of these variables is limited to the backend configuration for the
layers in this environment.
*/

role_arn       = "CHANGEME" # (the role Terraform will assume to work with S3 remote state)
region         = "CHANGEME" # (the region where the S3 remote state bucket is)
bucket         = "CHANGEME"
dynamodb_table = "CHANGEME"
