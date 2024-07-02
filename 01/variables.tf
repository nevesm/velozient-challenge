variable "project" {
  description = "The name of the project."
  default     = "velozient-app"
}

variable "region" {
  description = "The region in which the resources will be created."
  default     = "Brazil South"
}

variable "tags" {
  description = "A map of tags to add to all resources."
  default = {
    environment   = "prod"
    project       = "velozient-app"
    business_unit = "erp"
    cost_center   = "2594"
    repository    = "nevesm/velozient-challenge"
  }
}

variable "vpc_address_space" {
  description = "The address space to use for the VPC."
  default = {
    main = ["10.0.0.0/16"]
  }
}

variable "subnet_prefixes" {
  description = "The list of prefixes to use for the subnets."
  default = {
    web      = ["10.0.1.0/24"]
    app      = ["10.0.2.0/24"]
    database = ["10.0.3.0/24"]
  }
}

variable "vm_pool" {
  description = "The number of VMs to create."
  default = {
    web = 2
    app = 1
  }
}

variable "vm_size" {
  description = "The size of the VMs to create."
  default = {
    web = "Standard_B1s"
    app = "Standard_B1s"
  }
}