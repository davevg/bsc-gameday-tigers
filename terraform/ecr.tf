module "ecr" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.2.1"

  repository_name = replace(var.project, "-", "_")
  repository_image_tag_mutability = "MUTABLE"
  repository_image_scan_on_push = false

  repository_lifecycle_policy = jsonencode({
    rules = [
      {
        action = {
          type = "expire"
        }
        description  = "lifecycle"
        rulePriority = 1
        selection = {
          countNumber = 5
          countType   = "imageCountMoreThan"
          tagStatus   = "untagged"
        }
      }
    ]
  })

}