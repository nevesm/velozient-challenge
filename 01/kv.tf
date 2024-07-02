resource "azurerm_key_vault" "main" {
  name                       = format("%s-kv", var.project)
  location                   = var.region
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = data.azurerm_client_config.current.tenant_id
  sku_name                   = "premium"
  soft_delete_retention_days = 7

  access_policy {
    tenant_id = data.azurerm_client_config.current.tenant_id
    object_id = data.azurerm_client_config.current.object_id

    key_permissions = [
      "Create",
      "Get",
      "List"
    ]

    secret_permissions = [
      "Set",
      "Get",
      "Delete",
      "Purge",
      "Recover"
    ]
  }
  tags = var.tags
}

resource "azurerm_key_vault_secret" "mssql_password" {
  name         = format("%s-mssql-password", var.project)
  value        = random_password.mssql_password.result
  key_vault_id = azurerm_key_vault.main.id
  tags         = var.tags
}

resource "azurerm_key_vault_secret" "mssql_user" {
  name         = format("%s-mssql-user", var.project)
  value        = azurerm_mssql_server.main.administrator_login
  key_vault_id = azurerm_key_vault.main.id
  depends_on   = [azurerm_mssql_server.main]
  tags         = var.tags
}