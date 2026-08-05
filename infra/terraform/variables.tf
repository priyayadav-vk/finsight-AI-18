variable "do_token" {
  description = "DigitalOcean API token (set via env or terraform.tfvars)."
  type        = string
  sensitive   = true
}

variable "droplet_name" {
  description = "Name of the droplet"
  type        = string
  default     = "finsightai"
}

variable "region" {
  description = "DigitalOcean region"
  type        = string
  default     = "nyc3"
}

variable "size" {
  description = "Droplet size slug"
  type        = string
  default     = "s-1vcpu-2gb"
}

variable "image" {
  description = "Droplet image"
  type        = string
  default     = "ubuntu-22-04-x64"
}

variable "ssh_keys" {
  description = "Optional list of SSH key IDs or fingerprints already uploaded to DO (use null or [])."
  type        = list(string)
  default     = []
}

variable "ssh_pub_key" {
  description = "Public SSH key contents (used by cloud-init for the created user)."
  type        = string
  default     = ""
}

variable "repo_url" {
  description = "HTTPS Git repository URL to clone"
  type        = string
  default     = "https://github.com/priyayadav-vk/FinSightAI"
}

variable "repo_branch" {
  description = "Optional git branch to check out"
  type        = string
  default     = "main"
}

variable "app_user" {
  description = "Linux username that will be created on the droplet to run the app"
  type        = string
  default     = "finsight"
}
