# CockroachDB Cluster Deployment

Production-grade Ansible playbook for deploying a secure CockroachDB cluster.

## Architecture

- Multi-node CockroachDB cluster (3+ nodes recommended)
- Hardware requirements per node:
  - RAM: 2GB minimum
  - CPU: 2 cores minimum
  - Storage: SSD recommended
- Security features:
  - UFW firewall configuration
  - SSL/TLS encryption (optional)
  - Fail2ban
  - System hardening

## Prerequisites

1. Target nodes:
   - Ubuntu/Debian OS
   - SSH access with sudo privileges
   - Python 3.x installed

2. Control machine:
   - Ansible 2.9+
   - SSH key access to target nodes

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd cockroachdb-ansible
```

2. Configure your inventory:
```bash
cp inventories/production/hosts.yml.example inventories/production/hosts.yml
```

Edit `hosts.yml`:
```yaml
[cockroachdb_cluster]
node1 ansible_host=192.168.1.160 ansible_ssh_private_key_file=~/.ssh/id_rsa
node2 ansible_host=192.168.1.161 ansible_ssh_private_key_file=~/.ssh/id_rsa
node3 ansible_host=192.168.1.162 ansible_ssh_private_key_file=~/.ssh/id_rsa
```

3. Set vault password:
```bash
echo "your_vault_password" > .vault_pass
```
4. Create vault.yml for database password:

bashCopycat > inventories/production/group_vars/all/vault.yml << EOL
---
vault_cockroachdb_admin_password: "your_safe_db_password"
EOL

# Encrypt the vault file
ansible-vault encrypt inventories/production/group_vars/all/vault.yml

5. Configure variables (if needed):
   - Edit `inventories/production/group_vars/all/main.yml`
   - Key settings:
     ```yaml
     cockroachdb:
       version: "24.3.2"
       http_port: 8080
       sql_port: 26258
       cluster_port: 26257
       max_memory: "25%"
       cache_size: "25%"
     ```

5. Run the playbook:
```bash
ansible-playbook site.yml -i inventories/production/hosts.yml --ask-become-pass
```

6. Initialize the cluster:
```bash
cockroach init --insecure --host=192.168.1.160:26257
```
Replace `192.168.1.160` with your node1's IP address

## Role Structure

- `common`: Base system configuration and dependencies
- `security`: Firewall, SSL/TLS, and system hardening
- `cockroachdb`: Core database installation and configuration
- `startdb`: Database initialization and startup
- `monitoring`: Prometheus and Grafana setup (optional)

## Configuration Options

### SSL/TLS Setup

1. Enable SSL in group_vars:
```yaml
security:
  ssl:
    enabled: true
```

2. Certificates will be automatically generated in `/opt/cockroachdb/certs/`

### Memory Configuration

Adjust in group_vars:
```yaml
cockroachdb:
  max_memory: "75%"  # Total memory limit
  cache_size: "25%"  # Cache size
```

### Network Security

Default allowed networks:
```yaml
trusted_networks: "192.168.1.0/24"
admin_networks: "192.168.1.0/24"
monitoring_networks: "192.168.1.0/24"
```

## Post-Installation

1. Verify cluster status:
```bash
cockroach node status --insecure --host=<node1-ip>:26258
```

2. Access Admin UI:
   - URL: http://<node1-ip>:8080
   - Default credentials:
     - Username: root
     - Password: Set in vault_cockroachdb_admin_password

## Common Operations

### Add New Node

1. Add node to inventory
2. Run playbook with new node
```bash
ansible-playbook site.yml -i inventories/production/hosts.yml --limit=new_node
```

### Update CockroachDB Version

1. Update version in group_vars:
```yaml
cockroachdb:
  version: "24.3.2"
```

2. Run playbook with --tags upgrade:
```bash
ansible-playbook site.yml -i inventories/production/hosts.yml --tags upgrade
```

## Troubleshooting

### Node Won't Start

1. Check logs:
```bash
tail -f /var/log/cockroachdb/cockroach.log
```

2. Verify ports:
```bash
netstat -tlpn | grep -E '8080|26257|26258'
```

3. Clean restart:
```bash
ansible-playbook site.yml -i inventories/production/hosts.yml --tags clean,startdb
```

### SSL Certificate Issues

Reset certificates:
```bash
ansible-playbook site.yml -i inventories/production/hosts.yml --tags security --extra-vars="regenerate_certs=true"
```

## Performance Tuning

Key system settings (automatically configured):
```yaml
vm.swappiness: 1
vm.max_map_count: 262144
net.core.somaxconn: 65535
net.ipv4.tcp_max_syn_backlog: 65535
```

File limits:
```yaml
nofile: 65536
nproc: 32768
```

## Backup and Recovery

Backup database:
```bash
cockroach backup database defaultdb into 's3://bucket-name' with revision_history;
```

Restore:
```bash
cockroach restore database defaultdb from 's3://bucket-name';
```
