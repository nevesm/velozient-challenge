resource "azurerm_network_security_group" "web" {
  name                = "web-nsg"
  location            = var.region
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "allow-http"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "80"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  tags = var.tags
}

resource "azurerm_network_security_group" "app" {
  name                = "app-nsg"
  location            = var.region
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "allow-app"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "8080"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  tags = var.tags
}

resource "azurerm_network_security_group" "database" {
  name                = "db-nsg"
  location            = var.region
  resource_group_name = azurerm_resource_group.main.name

  security_rule {
    name                       = "allow-sql"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "1433"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  tags = var.tags
}


resource "azurerm_subnet_network_security_group_association" "web" {
  subnet_id                 = azurerm_subnet.main["web"].id
  network_security_group_id = azurerm_network_security_group.web.id
}

resource "azurerm_subnet_network_security_group_association" "app" {
  subnet_id                 = azurerm_subnet.main["app"].id
  network_security_group_id = azurerm_network_security_group.app.id
}

resource "azurerm_subnet_network_security_group_association" "database" {
  subnet_id                 = azurerm_subnet.main["database"].id
  network_security_group_id = azurerm_network_security_group.database.id
}