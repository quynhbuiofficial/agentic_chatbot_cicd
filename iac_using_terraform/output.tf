# Output Frontend Public IP
output "aws_frontend_ip" {
  value = aws_instance.frontend_ec2.public_ip
}
# # Ouput Frontend public dns
# output "aws_frontend_dns" {
#   value = aws_instance.frontend_ec2.public_dns
# }

# #Output Frontend DNS loadbalancer
# output "lb_dns_name" {
#   value = aws_lb.alb_ne.dns_name
# }

# # Output backend Private IP
# output "backend_private_ips" {
#   value       = aws_instance.backend_ec2.private_ip
# }

# # Output service Private IP
# output "services_private_ips" {
#   description = "List of private IPs for services EC2 instances"
#   value       = [for instance in aws_instance.services_ec2 : instance.private_ip]
# }
output "elasticsearch_private_ip" {
  value = aws_instance.services_ec2[0].private_ip
}
# output "neo4j_private_ip" {
#   value = aws_instance.services_ec2[2].private_ip
# }
# output "mcp_private_ip" {
#   value = aws_instance.services_ec2[1].private_ip
# }








