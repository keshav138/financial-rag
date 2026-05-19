output "instance_public_ip"{
    description = "Public IP of the EC2 Instance"
    value = aws_instance.financial_rag.public_ip
}

output "app_url"{
    description = "Financial RAG API URL"
    value = "http://${aws_instance.financial_rag.public_ip}:8000"
}

output "grafana_url"{
    description = "Grafana URL"
    value = "http://${aws_instance.financial_rag.public_ip}:3000"
}