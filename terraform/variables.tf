variable "aws_region" {
    default = "ap-south-1"
}

variable "ami_id"{
    description = "Ubuntu 22.04 LTS - ap-south-1"
    default     = "ami-0388e3ada3d9812da"
}

variable "instance_type" {
    description = "EC2 Instance type"
    default = "m7i-flex.large"
}

variable "public_key_path" {
    description = "Path to local SSH key"
    default = "~/.ssh/id_rsa.pub"
}

variable "groq_api_key" {
    description = "GROQ API key"
    sensitive = true
}

variable "hf_token" {
    description = "HuggingFace Token"
    sensitive = true
}

variable "dockerhub_image" {
    description = "Dockerhub image to deploy"
    default =  "keshavmaiya/financial-rag:latest"
}