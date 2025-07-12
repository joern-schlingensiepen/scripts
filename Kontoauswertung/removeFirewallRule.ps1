$ruleName = "Flask Webserver 3580"

$rule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($rule) {
    Remove-NetFirewallRule -DisplayName $ruleName
    Write-Host "Firewall-Regel '$ruleName' wurde entfernt."
} else {
    Write-Host "Keine Firewall-Regel mit dem Namen '$ruleName' gefunden."
}
