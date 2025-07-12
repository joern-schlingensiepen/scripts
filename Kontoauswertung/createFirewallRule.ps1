$ruleName = "Flask Webserver 3580"
$port = 3580

# Prüfen, ob die Regel bereits existiert
$existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue

if ($existingRule) {
    Write-Host "Firewall-Regel '$ruleName' existiert bereits."
} else {
    New-NetFirewallRule -DisplayName $ruleName `
        -Direction Inbound `
        -LocalPort $port `
        -Protocol TCP `
        -Action Allow `
        -Profile Any

    Write-Host "Firewall-Regel '$ruleName' wurde erstellt und Port $port geöffnet."
}
