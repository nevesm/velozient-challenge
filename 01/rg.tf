resource "azurerm_resource_group" "main" {
  name     = var.project
  location = var.region
}