resource "azurerm_virtual_network" "main" {
  name                = "main-vnet"
  address_space       = var.vpc_address_space["main"]
  location            = var.region
  resource_group_name = azurerm_resource_group.main.name
  tags                = var.tags
}

resource "azurerm_subnet" "main" {
  for_each             = var.subnet_prefixes
  name                 = format("%s-subnet", each.key)
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = each.value
}