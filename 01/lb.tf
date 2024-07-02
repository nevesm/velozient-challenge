locals {
  backend_address_pool_name      = format("%s-beap", var.project)
  frontend_port_name             = format("%s-feport", var.project)
  frontend_ip_configuration_name = format("%s-feip", var.project)
  http_setting_name              = format("%s-be-htst", var.project)
  http_listener_name             = format("%s-http", var.project)
  request_routing_rule_name      = format("%s-rqrt", var.project)
  redirect_configuration_name    = format("%s-rdrcfg", var.project)
}

resource "azurerm_public_ip" "lb" {
  name                = var.project
  location            = var.region
  resource_group_name = azurerm_resource_group.main.name
  allocation_method   = "Static"
  sku                 = "Standard"
  tags                = var.tags
}

resource "azurerm_lb" "main" {
  name                = format("%s-lb", var.project)
  location            = var.region
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"

  frontend_ip_configuration {
    name                 = "PublicIPAddress"
    public_ip_address_id = azurerm_public_ip.lb.id
  }
}

resource "azurerm_lb_rule" "http" {
  loadbalancer_id                = azurerm_lb.main.id
  name                           = "HttpRule"
  protocol                       = "Tcp"
  frontend_port                  = 80
  backend_port                   = 80
  frontend_ip_configuration_name = "PublicIPAddress"
  backend_address_pool_ids       = [azurerm_lb_backend_address_pool.main.id]
}

resource "azurerm_lb_rule" "https" {
  loadbalancer_id                = azurerm_lb.main.id
  name                           = "HttpsRule"
  protocol                       = "Tcp"
  frontend_port                  = 443
  backend_port                   = 443
  frontend_ip_configuration_name = "PublicIPAddress"
  backend_address_pool_ids       = [azurerm_lb_backend_address_pool.main.id]
}

resource "azurerm_lb_backend_address_pool" "main" {
  loadbalancer_id = azurerm_lb.main.id
  name            = local.backend_address_pool_name
}

resource "azurerm_network_interface_backend_address_pool_association" "web" {
  count                   = var.vm_pool["web"]
  network_interface_id    = azurerm_network_interface.web[count.index].id
  ip_configuration_name   = "internal"
  backend_address_pool_id = azurerm_lb_backend_address_pool.main.id
}