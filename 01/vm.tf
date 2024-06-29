resource "azurerm_linux_virtual_machine" "web" {
  count               = var.vm_pool["web"]
  name                = format("web-vm-%s", count.index)
  location            = var.region
  resource_group_name = azurerm_resource_group.main.name
  network_interface_ids = [
    azurerm_network_interface.web[count.index].id,
  ]
  size           = var.vm_size
  admin_username = "sre"
  
  admin_ssh_key {
    username   = "sre"
    public_key = file("ssh/sre.pub")
  }
  
  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }
  
  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  tags = var.tags
}

resource "azurerm_linux_virtual_machine" "app" {
  count                 = var.vm_pool["app"]
  name                  = format("app-vm-%s", count.index)
  location              = var.region
  resource_group_name   = azurerm_resource_group.main.name
  network_interface_ids = [azurerm_network_interface.app[count.index].id]
  size                  = var.vm_size
  admin_username        = "sre"
  
  admin_ssh_key {
    username   = "sre"
    public_key = file("ssh/sre.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  tags = var.tags
}

resource "azurerm_network_interface" "web" {
  count               = var.vm_pool["web"]
  name                = format("web-nic-%s", count.index)
  location            = var.region
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main["web"].id
    private_ip_address_allocation = "Dynamic"
  }
  tags = var.tags
}

resource "azurerm_network_interface" "app" {
  count               = var.vm_pool["app"]
  name                = format("app-nic-%s", count.index)
  location            = var.region
  resource_group_name = azurerm_resource_group.main.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.main["app"].id
    private_ip_address_allocation = "Dynamic"
  }
  tags = var.tags
}