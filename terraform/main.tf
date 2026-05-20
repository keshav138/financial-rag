terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~>5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# security group
resource "aws_security_group" "financial_rag_sg" {
  name        = "financial-rag-sg"
  description = "Security group for Financial Rag Group"

  # SSH
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  #  FastAPI
  ingress {
    from_port   = 8000
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Prometheus
  ingress {
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Grafana
  ingress {
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # allow all outbound to connect to hg and groq
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# key-pair
resource "aws_key_pair" "financial_rag_key" {
  key_name   = "financial-rag-key"
  public_key = file(var.public_key_path)
}

# EC2 Instance
resource "aws_instance" "financial_rag" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  key_name               = aws_key_pair.financial_rag_key.key_name
  vpc_security_group_ids = [aws_security_group.financial_rag_sg.id]

  user_data = <<-EOF
        #!/bin/bash
        apt-get update -y
        apt-get install -y docker.io docker-compose
        systemctl start docker
        systemctl enable docker

        #create directory
        mkdir -p /app
        cd /app

        #create .env file
        cat > .env <<-ENVFILE
        GROQ_API_KEY=${var.groq_api_key}
        HUGGINGFACE_API_TOKEN=${var.hf_token}
        CHROMA_PERSIST_DIR=./chroma_db
        COLLECTION_NAME=financial_docs
        ENVFILE

        #create docker-compose.yml pulling from dockerhub
        cat > docker-compose.yml <<-COMPOSEFILE
        version: "3.8"
        services:
          app:
            image: ${var.dockerhub_image}
            ports:
              - "8000:8000"
            volumes:
              - ./chroma_db:/app/chroma_db
            env_file:
              - .env

          prometheus:
            image: prom/prometheus:latest
            ports:
              - "9090:9090"
            volumes:
              - ./prometheus.yml:/etc/prometheus/prometheus.yml
              - prometheus_data:/prometheus
            command:
              - "--config.file=/etc/prometheus/prometheus.yml"

          grafana:
            image: grafana/grafana:latest
            ports:
              - "3000:3000"
            volumes:
              - grafana_data:/var/lib/grafana
            environment:
              - GF_SECURITY_ADMIN_PASSWORD=admin
              - GF_SECURITY_ADMIN_USER=admin
            depends_on:
              - prometheus

        volumes:
          prometheus_data:
          grafana_data:
        COMPOSEFILE

        # create prometheus file
        cat > prometheus.yml <<-PROMFILE
        global:
          scrape_interval: 15s
        scrape_configs:
          - job_name: "financial-rag"
            static_configs:
              - targets: ["app:8000"]
        PROMFILE

        # pull and stop
        docker-compose up -d
    EOF

  tags = {
    Name = "financial-rag-server"
  }
}

