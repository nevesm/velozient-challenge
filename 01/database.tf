resource "azurerm_mssql_server" "main" {
  name                         = format("%s-sql-server", var.project)
  resource_group_name          = azurerm_resource_group.main.name
  location                     = var.region
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = random_password.mssql_password.result
  tags                         = var.tags
}

resource "azurerm_mssql_database" "main" {
  name         = format("%s-sql-database", var.project)
  server_id    = azurerm_mssql_server.main.id
  collation    = "SQL_Latin1_General_CP1_CI_AS"
  license_type = "LicenseIncluded"
  max_size_gb  = 2
  sku_name     = "Basic"
  enclave_type = "VBS"
  tags         = var.tags
}

resource "random_password" "mssql_password" {
  length           = 16
  special          = true
  override_special = "!#$%&*()-_=+[]{}<>:?"
}