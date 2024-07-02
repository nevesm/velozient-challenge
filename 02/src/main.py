from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient
import requests
import json

# Initialize Azure clients
credential = DefaultAzureCredential()
subscription_id = ''

compute_client = ComputeManagementClient(credential, subscription_id)
monitor_client = MonitorManagementClient(credential, subscription_id)
resource_client = ResourceManagementClient(credential, subscription_id)

def list_virtual_machines():
    print("Listing virtual machines...")
    vms = compute_client.virtual_machines.list_all()
    for vm in vms:
        print(f"💻 VM Name: {vm.name} | Location: {vm.location} | VM Size: {vm.hardware_profile.vm_size} | OS: {vm.storage_profile.os_disk.os_type} | ID: {vm.vm_id}")

def list_alerts():
    print("Listing alerts...")
    metricAlerts = monitor_client.metric_alerts.list_by_subscription()
    for alert in metricAlerts:
        alertStatus = get_metric_alert_status(subscription_id, alert.id.split('/')[4], alert.name)
        print(f"📊 Alert Name: {alert.name} | Status: {alertStatus} | Enabled: {alert.enabled} | Severity: {alert.severity} | Target Resource Type: {alert.target_resource_type} | Scopes: {alert.scopes}")
    logActivityAlerts = monitor_client.activity_log_alerts.list_by_subscription_id()
    for alert in logActivityAlerts:
        alertStatus = get_activity_log_alert_status(subscription_id, alert.id.split('/')[4], alert.name)
        print(f"📄 Alert Name: {alert.name} | Status: {alertStatus} | Enabled: {alert.enabled} | Scopes: {alert.scopes}")

def metric_alert():
    resourceGroupsList = [rg.name for rg in resource_client.resource_groups.list()]
    resourceGroupCompleter = WordCompleter(resourceGroupsList, ignore_case=True)
    resourceGroup = prompt("Choose a resource group: ", completer=resourceGroupCompleter)
    description = prompt("Type the description of the rule:")
    severity = prompt("Type the severity of the rule (1, 2, 3): ")
    evaluationFrequency = prompt("Type the evaluation frequency in timedelta format (PT1M, PT5M, PT15M, PT30M, PT1H): ", completer=WordCompleter(['PT1M', 'PT5M', 'PT15M', 'PT30M', 'PT1H'], ignore_case=True))
    targetResourceType = prompt("Type the target resource type (only 'Microsoft.Compute/virtualMachines' available now): ", completer=WordCompleter(['Microsoft.Compute/virtualMachines'], ignore_case=True))
    targetResourceRegion = prompt("Type the target resource region (brazilsouth): ", completer=WordCompleter(['brazilsouth'], ignore_case=True))
    metrics = monitor_client.metric_definitions.list_at_subscription_scope("brazilsouth", "Microsoft.Compute/virtualMachines")
    listOfMetrics = []
    for metric in metrics:
        listOfMetrics.append(metric.name.value)
    metric_completer = WordCompleter(listOfMetrics, ignore_case=True)
    while True:
        metricName = prompt("Choose a metric name: ", completer=metric_completer)
        if metricName in listOfMetrics:
            metricOperator = prompt("Type the metric operator (GreaterThan, LessThan, GreaterOrLessThan): ", completer=WordCompleter(['GreaterThan', 'LessThan', 'GreaterOrLessThan'], ignore_case=True))
            timeAggregation = prompt("Type the time aggregation (Average, Count, Maximum, Minimum, Total): ", completer=WordCompleter(['Average', 'Count', 'Maximum', 'Minimum', 'Total'], ignore_case=True))
            metricCriteriaName = prompt("Type the metric criteria name (example: High_CPU_80): ")
            threshold = prompt("Type the threshold value (number): ")
            alertName = prompt("Type the alert name (example: [VMs][payments] High CPU Usage): ")
            metric_alert = monitor_client.metric_alerts.create_or_update(
                resourceGroup,
                alertName,
                {
                "location": "global",
                "description": description,
                "severity": severity,
                "enabled": True,
                "scopes": [
                    f"/subscriptions/{subscription_id}"
                ],
                "evaluation_frequency": evaluationFrequency,
                "window_size": "PT15M",
                "target_resource_type": targetResourceType,
                "target_resource_region": targetResourceRegion,
                "criteria": {
                    "odata.type": "Microsoft.Azure.Monitor.MultipleResourceMultipleMetricCriteria",
                    "all_of": [
                    {
                        "criterion_type": "DynamicThresholdCriterion",
                        "name": metricCriteriaName,
                        "metric_name": metricName,
                        "metric_namespace": "microsoft.compute/virtualmachines",
                        "operator": metricOperator,
                        "time_aggregation": timeAggregation,
                        "alert_sensitivity": "Medium",
                        "threshold": threshold,
                        "failing_periods": {
                        "number_of_evaluation_periods": "4",
                        "min_failing_periods_to_alert": "4"
                        },
                    }
                    ]
                },
                "auto_mitigate": False,
                "actions": []
                }
            )
            print("Create metric alert:\n{}".format(metric_alert))
            break

def activity_log_alert():
    resourceGroupsList = [rg.name for rg in resource_client.resource_groups.list()]
    resourceGroupCompleter = WordCompleter(resourceGroupsList, ignore_case=True)
    resourceGroup = prompt("Choose a resource group: ", completer=resourceGroupCompleter)
    alertName = prompt("Type the alert name (example: [Error] Azure SQL): ")
    alertDescription = prompt("Type the alert description: (example: Alert for Azure SQL errors): ")
    category = prompt("Type the category of the activity log event (example: Administrative, ServiceHealth, Alert): ", completer=WordCompleter(['Administrative', 'ServiceHealth', 'Alert'], ignore_case=True))
    numberOfAdditionalFields = prompt("Type the number of additional fields to filter: ")
    allOf = [{"field": "category", "equals": category}]
    for i in range(int(numberOfAdditionalFields)):
        field = prompt(f"The name of the Activity Log event's field that this condition will examine. The possible values for this field are (case-insensitive): 'resourceId', 'category', 'caller', 'level', 'operationName', 'resourceGroup', 'resourceProvider', 'status', 'subStatus', 'resourceType', or anything beginning with 'properties' {i+1}: ", completer=WordCompleter(['resourceId', 'category', 'caller', 'level', 'operationName', 'resourceGroup', 'resourceProvider', 'status', 'subStatus', 'resourceType', 'properties'], ignore_case=True))
        equals = prompt(f"The value of the event's field will be compared to this value (case-insensitive) to determine if the condition is met. {field}: ")
        allOf.append({"field": field, "equals": equals})
    log_alert = monitor_client.activity_log_alerts.create_or_update(
        resourceGroup,
        alertName,
        {
          "location": "Global",
          "scopes": [
            "subscriptions/" + subscription_id
          ],
          "enabled": True,
          "condition": {
            "all_of": allOf
          },
          "actions": {
            "action_groups": [
            ]
          },
          "description": alertDescription
        }
    )
    print("Create activity log alert:\n{}".format(log_alert))
    return True

def create_new_alert():
    actions = ['metric', 'activity_log']
    actionCompleter = WordCompleter(actions, ignore_case=True)
    while True:
        action = prompt("Choose an alert type: 'metric' or 'activity_log': ", completer=actionCompleter)
        if action == 'metric':
            metric_alert()
            break
        elif action == 'activity_log':
            activity_log_alert()
            break
        else:
            print("Invalid alert type. Please choose from the list.")

def delete_alert():
    print("Fetching alerts...")
    while True:
        action = prompt("Choose an alert type to delete: 'metric' or 'activity_log': ", completer=WordCompleter(['metric', 'activity_log'], ignore_case=True))
        if action == 'metric':
                alerts = monitor_client.metric_alerts.list_by_subscription()
                alertDict = {alert.name: alert for alert in alerts}
                alertCompleter = WordCompleter(alertDict.keys(), ignore_case=True)
                alertName = prompt("Choose an alert to delete: ", completer=alertCompleter)
                selectedAlert = alertDict[alertName]
                resourceGroupName = selectedAlert.id.split('/')[4]
                monitor_client.metric_alerts.delete(resourceGroupName, alertName)
                break
        elif action == 'activity_log':
            alerts = monitor_client.activity_log_alerts.list_by_subscription_id()
            alertDict = {alert.name: alert for alert in alerts}
            alertCompleter = WordCompleter(alertDict.keys(), ignore_case=True)
            alertName = prompt("Choose an alert to delete: ", completer=alertCompleter)
            selectedAlert = alertDict[alertName]
            resourceGroupName = selectedAlert.id.split('/')[4]
            monitor_client.activity_log_alerts.delete(resourceGroupName, alertName)
            break
        else:
            print("Invalid alert type. Please choose from the list.")

def get_metric_alert_status(subscription_id, resource_group, alert_name):
    token = credential.get_token("https://management.azure.com/.default").token
    url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/microsoft.insights/metricAlerts/{alert_name}/status?api-version=2018-03-01"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        status_data = response.json()
        if status_data["value"][0]["properties"]["status"] == "Healthy":
            return "Healthy✅"
        else:
            return "Not Healthy🔥"
    else:
        print(f"Failed to get status for alert {alert_name}. Status code: {response.status_code}")

def get_activity_log_alert_status(subscription_id, resource_group, alert_name):
    token = credential.get_token("https://management.azure.com/.default").token
    url = f"https://management.azure.com/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/microsoft.insights/activityLogAlerts/{alert_name}?api-version=2017-04-01"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        alert_data = response.json()
        conditions = alert_data.get("properties", {}).get("conditions", {})
        if conditions:
            for condition in conditions:
                if condition.get("status") == "Active":
                    print(f"Activity log alert {alert_name} is currently active.")
                else:
                    print(f"Activity log alert {alert_name} is not active.")
        else:
            print(f"No conditions found for alert {alert_name}.")
    else:
        print(f"Failed to get status for alert {alert_name}. Status code: {response.status_code}")

def main():
    actions = ['list_vms', 'list_alerts', 'create_alert', 'delete_alert', 'exit']
    action_completer = WordCompleter(actions, ignore_case=True)
    print("""
        _    __     __            _            __                           _ __             _                ________    ____
        | |  / /__  / /___  ____  (_)__  ____  / /_   ____ ___  ____  ____  (_) /_____  _____(_)___  ____ _   / ____/ /   /  _/
        | | / / _ \/ / __ \/_  / / / _ \/ __ \/ __/  / __ `__ \/ __ \/ __ \/ / __/ __ \/ ___/ / __ \/ __ `/  / /   / /    / /  
        | |/ /  __/ / /_/ / / /_/ /  __/ / / / /_   / / / / / / /_/ / / / / / /_/ /_/ / /  / / / / / /_/ /  / /___/ /____/ /   
        |___/\___/_/\____/ /___/_/\___/_/ /_/\__/  /_/ /_/ /_/\____/_/ /_/_/\__/\____/_/  /_/_/ /_/\__, /   \____/_____/___/   
                                                                                                /____/                       
        """)
    print("This tool has auto-complete enabled. Press 'tab' to see the available options.\n\n\n")

    while True:
        action = prompt("Choose an action (list_vms, list_alerts, create_alert, delete_alert) or 'exit' to quit: ", completer=action_completer)
        if action == 'exit':
            print("Exiting...")
            break
        elif action == 'list_vms':
            list_virtual_machines()
        elif action == 'list_alerts':
            list_alerts()
        elif action == 'create_alert':
            create_new_alert()
        elif action == 'delete_alert':
            delete_alert()
        else:
            print("Invalid action. Please choose from the list.")

if __name__ == "__main__":
    main()
