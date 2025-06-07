# 🤖 Agentic Chatbot CI/CD Deployment to AWS with GitHub Actions

This project automates the CI/CD pipeline to deploy a full-stack **Agentic Chatbot System** to AWS EC2 using **Docker**, **Terraform**, and **GitHub Actions**. The system includes frontend, backend, Elasticsearch, Neo4j, and an MCP server, designed to run efficiently within a secure VPC and subnet configuration.

---

## 📌 Architecture Diagrams

### 🔷 Terraform Infrastructure Layout

![Terraform Infrastructure](./path/to/eddf8a11-6829-477b-b244-753a34bf57f7.png)

- **VPC**: `10.0.0.0/16`
- **Public Subnet**: `10.0.0.0/22`
- **Private Subnet-01**: `10.0.4.0/22`
- **Private Subnet-02**: `10.0.8.0/22`
- **NAT Gateway**: Allow private subnets to access the internet securely
- **S3 Bucket**: Store Terraform remote backend state

---

### 🔶 Chatbot Deployment Layout

![Chatbot Deployment](./path/to/ef1bb8f8-0222-41a2-b148-088ffd3091f8.png)

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

| Secret Name             | Description                                |
|-------------------------|--------------------------------------------|
| `AWS_ACCESS_KEY_ID`     | AWS Access Key ID dùng để truy cập AWS API |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key                      |
| `DOCKER_HUB_TOKEN`      | Token để đẩy/pull image từ Docker Hub      |
| `KEYPAIR_PRIVATE`       | Private key (dạng `.pem`) để SSH vào EC2   |
| `KEYPAIR_PUBLIC`        | Public key tương ứng cho EC2 Key Pair       |
| `LANGFUSE_PUBLIC_KEY`   | Public API Key của Langfuse                |
| `LANGFUSE_SECRET_KEY`   | Secret API Key của Langfuse                |
| `LEQUYNHLE_GITHUB_TOKEN`| GitHub token (Personal Access Token) để truy cập GHCR và API |

---

## 🚀 Setup & Deployment

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/agentic_chatbot_cicd.git
cd agentic_chatbot_cicd

### 2. Initialize Terraform Infrastructure

``` bash
cd terraform
terraform init
terraform apply

This will:
Create VPC, public/private subnets
Attach NAT and Internet Gateways
Provision EC2 instance
Set up S3 backend

### 3. Configure GitHub Secrets
Settings → Secrets and variables → Actions → New repository secret
Add:
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
DOCKER_HUB_TOKEN
...

### 4. CI/CD Workflow via GitHub Actions
The provided GitHub Actions workflow will:
1. Build Docker images
2. Push to Docker Hub
3. SSH into EC2 instance
4. Pull and deploy the containers using docker like docker compose

# 🧠 Author
## Developed and maintained by @quynhbuiofficial
