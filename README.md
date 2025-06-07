# 🤖 Agentic Chatbot CI/CD Deployment to AWS with GitHub Actions

This project automates the CI/CD pipeline to deploy a full-stack **Agentic Chatbot System** to AWS EC2 using **Docker**, **Terraform**, and **GitHub Actions**. The system includes frontend, backend, Elasticsearch, Neo4j, and an MCP server, designed to run efficiently within a secure VPC and subnet configuration.

<div align="center">
  <img src="https://github.com/user-attachments/assets/d028957b-a4b0-4559-bee8-8c2859989013" width="80%">
  <img src="https://github.com/user-attachments/assets/af79b5f2-0733-4919-aa0e-a2293f0fd8f7" width="80%">
</div>

---

## 📌 Architecture Diagrams

### 🔷 Terraform Infrastructure Layout
- **VPC**: `10.0.0.0/16`
- **Public Subnet**: `10.0.0.0/22`
- **Private Subnet-01**: `10.0.4.0/22`
- **Private Subnet-02**: `10.0.8.0/22`
- **Application Load Balancer**: Distributes traffic evenly across backend services
- **NAT Gateway**: Allow private subnets to access the internet securely
- **S3 Bucket**: Store Terraform remote backend state

---

### 🔶 Chatbot Deployment Layout
- **Frontend**:
  - Exposed via port `5173` from the internet
- **Application Load Balancer (ALB)**:
  - Listens on port `80`, forwards to backend on port `9999`
- **Backend**:
  - Communicates with:
    - **MCP Server**: port `1234`
    - **Elasticsearch**: port `9200`
    - **Neo4j**: port `7687`

---

## 🛠️ Prerequisites

Trong GitHub repo, bạn cần cấu hình các **Secrets** sau để CI/CD hoạt động:

| Secret Name              | Description                                                     |
|--------------------------|-----------------------------------------------------------------|
| `AWS_ACCESS_KEY_ID`      | AWS Access Key ID used to access AWS API                        |
| `AWS_SECRET_ACCESS_KEY`  | AWS Secret Access Key                                           |
| `DOCKER_HUB_TOKEN`       | Token used to push/pull Docker images from Docker Hub           |
| `KEYPAIR_PRIVATE`        | Private key (`.pem` format) used for SSH access to EC2          |
| `KEYPAIR_PUBLIC`         | Corresponding public key for the EC2 Key Pair                   |
| `LANGFUSE_PUBLIC_KEY`    | Langfuse Public API Key                                         |
| `LANGFUSE_SECRET_KEY`    | Langfuse Secret API Key                                         |
| `LEQUYNHLE_GITHUB_TOKEN` | GitHub Personal Access Token used to access LLM for Chatbot |

---

## 🚀 Setup & Deployment

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/agentic_chatbot_cicd.git
cd agentic_chatbot_cicd
```

### 2. Initialize Terraform Infrastructure

``` 
cd terraform
terraform init
terraform apply
```

This will:
Create VPC, public/private subnets
Attach NAT and Internet Gateways
Provision EC2 instance
Set up S3, ALB

### 3. Configure GitHub Secrets
Settings → Secrets and variables → Actions → New repository secret
- Add:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - DOCKER_HUB_TOKEN
...

### 4. CI/CD Workflow via GitHub Actions
The provided GitHub Actions workflow will:
- 1. Build Docker images
- 2. Push to Docker Hub
- 3. SSH into EC2 instance
- 4. Pull and deploy the containers using docker like docker compose

# 🧠 Author
## Developed and maintained by @quynhbuiofficial
