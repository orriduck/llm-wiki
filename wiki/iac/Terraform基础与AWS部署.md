---
tags: [terraform, iac, aws, infrastructure]
---

# Terraform Basics & AWS Deployment / Terraform 基础与 AWS 资源部署

## What is Terraform? / 什么是 Terraform？

Terraform is an open-source Infrastructure-as-Code (IaC) tool created by HashiCorp. It lets you define cloud infrastructure using a declarative configuration language (HCL — HashiCorp Configuration Language), and then provisions, changes, and destroys that infrastructure through API calls to your chosen provider.

> Terraform 是 HashiCorp 创建的开源基础设施即代码（IaC）工具。你用声明式配置语言（HCL）描述期望的基础设施状态，Terraform 负责通过各云厂商 API 完成资源的创建、变更与销毁。

**Core principle:** You describe **what** you want; Terraform figures out **how** to get there.

> **核心理念：** 你声明"期望状态"，Terraform 负责计算并执行变更路径。

---

## Key Concepts / 核心概念

### Providers / 提供商

A provider is a plugin that talks to a specific API (AWS, GCP, Azure, GitHub, etc.). Each provider exposes **resources** and **data sources**.

> Provider 是与特定 API（AWS、GCP、Azure、GitHub 等）通信的插件。每个 provider 暴露**资源（resource）**和**数据源（data source）**。

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}
```

### Resources / 资源

A resource is a single infrastructure object — an EC2 instance, S3 bucket, VPC, etc.

> Resource 是单个基础设施对象，例如 EC2 实例、S3 存储桶、VPC 等。

```hcl
resource "aws_s3_bucket" "my_bucket" {
  bucket = "my-example-bucket-2026"
}
```

### State / 状态文件

Terraform tracks the real-world resources it manages in a **state file** (`terraform.tfstate`). This is the source of truth for what Terraform thinks is deployed.

> Terraform 用**状态文件**（`terraform.tfstate`）追踪已部署的真实资源。状态文件是 Terraform 判断"当前现实"的依据。

**Best practice:** Store state remotely (S3 + DynamoDB lock) to enable team collaboration.

> **最佳实践：** 将状态存储在远端（S3 + DynamoDB 锁），以支持团队协作。

```hcl
terraform {
  backend "s3" {
    bucket         = "my-tf-state-bucket"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

### Variables & Outputs / 变量与输出

```hcl
variable "environment" {
  type        = string
  description = "Deployment environment (dev/staging/prod)"
  default     = "dev"
}

output "bucket_arn" {
  value       = aws_s3_bucket.my_bucket.arn
  description = "ARN of the created S3 bucket"
}
```

> 变量（`variable`）参数化配置；输出（`output`）暴露资源属性供外部引用或展示。

### Modules / 模块

A module is a reusable collection of resources. Every Terraform configuration is technically a module (the "root module").

> 模块是可复用的资源集合。每个 Terraform 配置本身就是一个模块（根模块）。

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
}
```

---

## Core Workflow / 核心工作流

```
terraform init      # Download providers & initialize backend
terraform plan      # Preview changes (dry run)
terraform apply     # Apply changes
terraform destroy   # Destroy all managed resources
```

> ```
> terraform init      # 下载 provider 插件、初始化后端
> terraform plan      # 预览变更（干跑）
> terraform apply     # 执行变更
> terraform destroy   # 销毁所有受管资源
> ```

---

## AWS Examples / AWS 部署示例

### Example 1: S3 Bucket with Versioning & Encryption / 示例 1：带版本控制和加密的 S3 存储桶

```hcl
resource "aws_s3_bucket" "data_lake" {
  bucket = "my-data-lake-${var.environment}"

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_versioning" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data_lake" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "data_lake" {
  bucket                  = aws_s3_bucket.data_lake.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

> 注意：S3 存储桶的版本控制、加密、公开访问封锁在 AWS Provider v4+ 中是独立资源，不再是 `aws_s3_bucket` 的内联块。

### Example 2: EC2 Instance with Security Group / 示例 2：EC2 实例与安全组

```hcl
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_security_group" "web" {
  name        = "web-sg-${var.environment}"
  description = "Allow HTTP/HTTPS inbound, all outbound"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "web-sg-${var.environment}"
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux_2.id
  instance_type          = "t3.micro"
  subnet_id              = module.vpc.public_subnets[0]
  vpc_security_group_ids = [aws_security_group.web.id]

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
    echo "<h1>Deployed via Terraform</h1>" > /var/www/html/index.html
  EOF

  tags = {
    Name        = "web-${var.environment}"
    Environment = var.environment
  }
}

output "web_public_ip" {
  value = aws_instance.web.public_ip
}
```

### Example 3: Lambda Function with IAM Role / 示例 3：Lambda 函数与 IAM 角色

```hcl
# IAM Role for Lambda
resource "aws_iam_role" "lambda_exec" {
  name = "lambda-exec-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda function (zip the source code first)
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_file = "${path.module}/src/handler.py"
  output_path = "${path.module}/dist/handler.zip"
}

resource "aws_lambda_function" "processor" {
  function_name    = "data-processor-${var.environment}"
  role             = aws_iam_role.lambda_exec.arn
  handler          = "handler.lambda_handler"
  runtime          = "python3.12"
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  timeout          = 30
  memory_size      = 256

  environment {
    variables = {
      ENVIRONMENT = var.environment
    }
  }

  tags = {
    ManagedBy = "terraform"
  }
}
```

### Example 4: RDS (PostgreSQL) / 示例 4：RDS PostgreSQL 数据库

```hcl
resource "aws_db_subnet_group" "main" {
  name       = "db-subnet-group-${var.environment}"
  subnet_ids = module.vpc.private_subnets

  tags = {
    Name = "db-subnet-group-${var.environment}"
  }
}

resource "aws_security_group" "rds" {
  name   = "rds-sg-${var.environment}"
  vpc_id = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]  # only allow web tier
  }
}

resource "aws_db_instance" "postgres" {
  identifier        = "myapp-db-${var.environment}"
  engine            = "postgres"
  engine_version    = "15.5"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  storage_encrypted = true

  db_name  = "myappdb"
  username = "dbadmin"
  password = var.db_password   # pass via TF_VAR_db_password env var

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]

  skip_final_snapshot     = var.environment != "prod"
  backup_retention_period = var.environment == "prod" ? 7 : 1
  multi_az                = var.environment == "prod"

  tags = {
    Environment = var.environment
  }
}
```

> 生产环境建议：启用 `multi_az`、`storage_encrypted`，设置合理的 `backup_retention_period`，并通过环境变量（`TF_VAR_db_password`）或 AWS Secrets Manager 传递密码，切勿写死在配置文件中。

---

## Project Layout Best Practices / 项目结构最佳实践

```
infra/
├── main.tf          # Root module: provider, backend
├── variables.tf     # Input variable declarations
├── outputs.tf       # Output value declarations
├── locals.tf        # Local computed values
├── versions.tf      # Required provider versions
├── terraform.tfvars # Variable values (gitignore if secrets)
└── modules/
    ├── networking/  # VPC, subnets, route tables
    ├── compute/     # EC2, ASG, ECS
    └── storage/     # S3, RDS, ElastiCache
```

> 推荐将不同资源类型拆分为子模块，根模块只负责组合与编排。`terraform.tfvars` 若包含敏感值应加入 `.gitignore`，使用 `terraform.tfvars.example` 作为模板提交到版本控制。

---

## Useful Commands / 常用命令速查

| Command / 命令 | Purpose / 用途 |
|---|---|
| `terraform init` | Initialize working directory / 初始化工作目录 |
| `terraform plan -out=tfplan` | Save plan to file / 保存计划到文件 |
| `terraform apply tfplan` | Apply saved plan / 应用已保存计划 |
| `terraform apply -target=aws_instance.web` | Apply only one resource / 只变更指定资源 |
| `terraform state list` | List managed resources / 列出受管资源 |
| `terraform state show aws_instance.web` | Show resource details / 查看资源详情 |
| `terraform import aws_s3_bucket.x my-bucket` | Import existing resource / 导入已有资源 |
| `terraform output -json` | Print outputs as JSON / 以 JSON 输出 |
| `terraform fmt -recursive` | Format all HCL files / 格式化所有 HCL 文件 |
| `terraform validate` | Check config syntax / 检查配置语法 |

---

## See Also / 相关页面

- [[OpenTofu简介与优势]] — Open-source Terraform fork with BSL-free licensing
- [[Terraform到OpenTofu迁移]] — Step-by-step migration guide
- [[S3]] — Deep dive on S3 concepts used above
- [[Lambda]] — Deep dive on Lambda concepts used above
