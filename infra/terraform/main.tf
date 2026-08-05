terraform {
  required_version = ">= 1.0.0"
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.26"
    }
  }
}

provider "digitalocean" {
  token = var.do_token
}

resource "digitalocean_droplet" "finsight" {
  name   = var.droplet_name
  region = var.region
  size   = var.size
  image  = var.image

  # Optional: pass SSH key IDs (fingerprints or integer IDs)
  ssh_keys = var.ssh_keys

  user_data = templatefile("${path.module}/cloud-init.yaml", {
    repo_url    = var.repo_url
    repo_branch = var.repo_branch
    app_user    = var.app_user
    ssh_pub_key = var.ssh_pub_key
  })

  tags = ["finsightai"]
}

output "droplet_ip" {
  description = "Public IPv4 address of the created Droplet"
  value       = digitalocean_droplet.finsight.ipv4_address
}
