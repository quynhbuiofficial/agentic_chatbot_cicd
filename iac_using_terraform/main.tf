provider "aws" {
  region = var.aws_region
}

# Create VPC
resource "aws_vpc" "vpc_ne" {
  cidr_block = var.vpc_cidr

  tags = {
    Name = "${var.enviroment}-vpc"
  }
}

locals {
  availability_zones = ["${var.aws_region}a", "${var.aws_region}b"]
}

# Public subnet
resource "aws_subnet" "public_subnets" {
  vpc_id                  = aws_vpc.vpc_ne.id
  count                   = length(var.public_subnets_cidr)
  cidr_block              = element(var.public_subnets_cidr, count.index)
  availability_zone       = element(local.availability_zones, count.index)
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.enviroment}-${element(local.availability_zones, count.index)}-public-subnet"
  }
}
# Private Subnet
resource "aws_subnet" "private_subnet" {
  vpc_id                  = aws_vpc.vpc_ne.id
  cidr_block              = var.private_subnet_cidr
  availability_zone       = local.availability_zones[0]
  map_public_ip_on_launch = false

  tags = {
    Name = "${var.enviroment}-${local.availability_zones[0]}-private-subnet"
  }
}

# IGW
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.vpc_ne.id
  tags = {
    "Name" = "${var.enviroment}-igw"
  }
}

# Elastic-IP for NAT
resource "aws_eip" "nat_eip" {
  depends_on = [aws_internet_gateway.igw]
}

# NAT gw
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat_eip.id
  subnet_id     = aws_subnet.public_subnets[0].id

  tags = {
    Name = "${var.enviroment}-nat"
  }
}

# Create Route table
resource "aws_route_table" "private_rtb" {
  vpc_id = aws_vpc.vpc_ne.id
  tags = {
    Name = "${var.enviroment}-private-rtb"
  }
}
resource "aws_route_table" "public_rtb" {
  vpc_id = aws_vpc.vpc_ne.id
  tags = {
    Name = "${var.enviroment}-public-rtb"
  }
}
# Configure public rtb
resource "aws_route" "public_internet_gw" {
  route_table_id         = aws_route_table.public_rtb.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.igw.id
}
# Configure private rtb
resource "aws_route" "private_internet_gw" {
  route_table_id         = aws_route_table.private_rtb.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_nat_gateway.nat.id
}
# Associate rtb 
resource "aws_route_table_association" "public_association" {
  count          = length(var.public_subnets_cidr)
  subnet_id      = aws_subnet.public_subnets[count.index].id
  route_table_id = aws_route_table.public_rtb.id
}
resource "aws_route_table_association" "private_association" {
  subnet_id      = aws_subnet.private_subnet.id
  route_table_id = aws_route_table.private_rtb.id
}

# Create Security Groups
resource "aws_security_group" "frontend_sg" {
  vpc_id      = aws_vpc.vpc_ne.id
  name        = "frontend sg"
  description = "SSH 22; Frontend 5173"
  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Frontend"
    from_port   = 5173
    to_port     = 5173
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    description = "Http"
    from_port   = 80
    to_port     = 80
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
    Name = "qbui-Frontend-sg"
  }
}
resource "aws_security_group" "alb_sg" {
  vpc_id      = aws_vpc.vpc_ne.id
  name        = "alb port 80"
  description = "http 80"
  ingress {
    description = "Http"
    from_port   = 80
    to_port     = 80
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
    Name = "qbui-alb-sg"
  }
}
resource "aws_security_group" "backend_sg" {
  vpc_id = aws_vpc.vpc_ne.id
  name   = "for backend"
  ingress {
    description     = "SSH"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.frontend_sg.id]
  }
  ingress {
    description     = "backend"
    from_port       = 9999
    to_port         = 9999
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "qbui-backend-sg"
  }
}
resource "aws_security_group" "mcp_server_sg" {
  vpc_id = aws_vpc.vpc_ne.id
  name   = "mcp_sv for backend"
  
  ingress {
    description     = "SSH"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.frontend_sg.id]
  }
  ingress {
    description     = "mcp"
    from_port       = 1234
    to_port         = 1234
    protocol        = "tcp"
    security_groups = [aws_security_group.backend_sg.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "qbui-mcp_server-sg"
  }
}

resource "aws_security_group" "elasticsearch_sg" {
  vpc_id = aws_vpc.vpc_ne.id
  name = "Elasticsearch for backend + mcp"

  ingress {
    description     = "SSH"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.frontend_sg.id]
  }
  ingress {
    description     = "BACKEND"
    from_port       = 9200
    to_port         = 9200
    protocol        = "tcp"
    security_groups = [aws_security_group.backend_sg.id]
  }
  ingress {
    description     = "MCP"
    from_port       = 9200
    to_port         = 9200
    protocol        = "tcp"
    security_groups = [aws_security_group.mcp_server_sg.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "qbui-elasticsearch-sg"
  }
}

resource "aws_security_group" "neo4j_sg" {
  vpc_id = aws_vpc.vpc_ne.id
  name = "Neo4j for backend"

  ingress {
    description     = "SSH"
    from_port       = 22
    to_port         = 22
    protocol        = "tcp"
    security_groups = [aws_security_group.frontend_sg.id]
  }
  ingress {
    description     = "neo4j"
    from_port       = 7687
    to_port         = 7687
    protocol        = "tcp"
    security_groups = [aws_security_group.backend_sg.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = {
    Name = "qbui-neo4j-sg"
  }
}


# #Generate a new private key (Trong luc tao ec2)
# resource "tls_private_key" "terraform_keypair" {
#   algorithm = "RSA"
#   rsa_bits  = 4096
# }
# # Create AWS Key Pair using the public key generated above
# resource "aws_key_pair" "terraform_keypair" {
#   key_name   = "terraform-keypair2"
#   public_key = tls_private_key.terraform_keypair.public_key_openssh
# }
# #To create a file or folder to save your Private Key
# resource "local_file" "terraform_keypair" {
#   content  = tls_private_key.terraform_keypair.private_key_pem
#   filename = "keypair2.pem"
# }

# Su Dung keypair da tao tu truoc
resource "aws_key_pair" "terraform_keypair" {
  key_name   = "keypair"
  public_key = var.keypair_public
}
# Create ec2
resource "aws_instance" "frontend_ec2" {
  depends_on    = [aws_security_group.frontend_sg, aws_subnet.public_subnets]
  ami           = "ami-084568db4383264d4"
  instance_type = "t2.micro"

  vpc_security_group_ids      = [aws_security_group.frontend_sg.id]
  subnet_id                   = aws_subnet.public_subnets[0].id
  associate_public_ip_address = true
  key_name                    = aws_key_pair.terraform_keypair.key_name
  # user_data                   = file("user_data.sh")

  root_block_device {
    volume_size           = 8
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name = var.ec2_frontend_name
  }
}
resource "aws_instance" "backend_ec2" {
  depends_on    = [aws_security_group.backend_sg, aws_subnet.public_subnets]
  ami           = "ami-084568db4383264d4"
  instance_type = "t2.medium"

  vpc_security_group_ids      = [aws_security_group.backend_sg.id]
  subnet_id                   = aws_subnet.private_subnet.id
  associate_public_ip_address = false
  key_name                    = aws_key_pair.terraform_keypair.key_name

  root_block_device {
    volume_size           = 13
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name = var.ec2_backend_name
  }
}

resource "aws_instance" "elasticsearch_ec2" {
  ami           = "ami-084568db4383264d4"
  instance_type = "t2.medium"

  vpc_security_group_ids      = [aws_security_group.elasticsearch_sg.id]
  subnet_id                   = aws_subnet.private_subnet.id
  associate_public_ip_address = false
  key_name                    = aws_key_pair.terraform_keypair.key_name

  root_block_device {
    volume_size           = 13
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name = "Elasticsearch_ec2"
  }
}

resource "aws_instance" "neo4j_ec2" {
  ami           = "ami-084568db4383264d4"
  instance_type = "t2.micro"

  vpc_security_group_ids      = [aws_security_group.neo4j_sg.id]
  subnet_id                   = aws_subnet.private_subnet.id
  associate_public_ip_address = false
  key_name                    = aws_key_pair.terraform_keypair.key_name

  root_block_device {
    volume_size           = 8
    volume_type           = "gp3"
    delete_on_termination = true
  }

  tags = {
    Name = "neo4j_ec2"
  }
}



# Creation of load balancer
resource "aws_lb_target_group" "backend_tg" {
  name        = "ALB-BACKEND-TG"
  port        = 9999 #9999
  protocol    = "HTTP"
  vpc_id      = aws_vpc.vpc_ne.id
  target_type = "instance"

  health_check {
    path                = "/"
    port                = 9999 #9999
    protocol            = "HTTP"
    interval            = 180        # mỗi 180 giây kiểm tra 1 lần
    timeout             = 10        # timeout sau 10 giây nếu không phản hồi
    healthy_threshold   = 2         # cần 2 lần liên tiếp thành công để considered healthy
    unhealthy_threshold = 10         # sau 10 lần thất bại thì considered unhealthy
    matcher             = "200"     # mã phản hồi mong muốn (có thể là "200-299")
  }
}
# Gắn EC2 vào target group
resource "aws_lb_target_group_attachment" "attach_backend1" {
  target_group_arn = aws_lb_target_group.backend_tg.arn
  target_id        = aws_instance.backend_ec2.id
  port             = 9999 # 9999
  depends_on = [
    aws_lb_target_group.backend_tg,
    aws_instance.backend_ec2,
  ]
}
# Tạo ALB
resource "aws_lb" "alb_ne" {
  name               = "chatbot-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb_sg.id]
  subnets            = [for subnet in aws_subnet.public_subnets : subnet.id]
}
# Listener
resource "aws_lb_listener" "listener_alb" {
  load_balancer_arn = aws_lb.alb_ne.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.backend_tg.arn
  }
}
