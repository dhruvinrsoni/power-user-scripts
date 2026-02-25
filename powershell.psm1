Write-Host "Running $($MyInvocation.MyCommand.Name)"
Write-Host "Path: $($MyInvocation.MyCommand.Path)"
function .. { cd '..' }

function ... {	cd /D '..\..' }

function a { type $DOSFILE_BASE; type $DOSFILE }

function b { 
	$argsString = $args -join ' '
    start cmd -Args "/c call get min && echo mvn clean install $argsString && call mvn clean install $argsString && get max && get message 'build successful at $TIME for $PWD' || get message 'build failed at $TIME for $PWD' & PAUSE" -WindowStyle Maximized 
}

function bye { Stop-Transcript -ErrorAction SilentlyContinue; exit; }  Set-Alias e bye -Force
function c { cls }

function cdm { Pop-Location; cdv @args; ls; }

function cdv { Push-Location -Path (Get-Variable -Name $args[0] -ValueOnly); ls; }

function cmdmax { Start-Process cmd.exe -WindowStyle Maximized }

function dirs { Get-Location -Stack }

function echov($varName) {
    if ($varValue = (Get-Variable -Name $varName -ErrorAction SilentlyContinue).Value) {
        $varValue | Tee-Object -Variable _ | Set-Clipboard
    } else {
        Write-Error "Variable '$varName' does not exist."
    }
}

function ex(){ explorer ($args -join ' ') }

function exv(){ explorer ((Get-Variable -Name $args[0] -ValueOnly) -join ' ') }

function func {
    param (
        [Parameter(Mandatory = $true)]
        [string]$FunctionName
    )

    $cmd = Get-Command $FunctionName -ErrorAction SilentlyContinue

    if (-not $cmd) {
        Write-Host "Function '$FunctionName' not found." -ForegroundColor Red
        return
    }

    Write-Host "`n--- Function Info for '$FunctionName' ---`n" -ForegroundColor Cyan

    Write-Host "Name: $($cmd.Name)"
    Write-Host "Type: $($cmd.CommandType)"
    Write-Host "Module: $($cmd.ModuleName)"
    Write-Host "Visibility: $($cmd.Visibility)"
    Write-Host "Definition:`n$($cmd.Definition)`n"

    if ($cmd.Parameters.Count -gt 0) {
        Write-Host "--- Parameters ---" -ForegroundColor Yellow
        foreach ($param in $cmd.Parameters.GetEnumerator()) {
            Write-Host "$($param.Key): $($param.Value.ParameterType.Name)"
        }
    }

    Write-Host "`n--- ScriptBlock ---" -ForegroundColor Yellow
    Write-Output $cmd.ScriptBlock

    Write-Host "`n--- Aliases ---" -ForegroundColor Yellow
    Get-Alias | Where-Object { $_.Definition -eq $FunctionName } | Format-Table Name, Definition
}

function g { git $args }

function git-ls { Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\.git\\' } | ForEach-Object { $_.FullName.Replace('$PWD.Path', '') } }

#
# GPG Sanity Check Function
# This works because it runs the gpg command directly in PowerShell,
# where we know the gpg-agent is working correctly.
#
function gpg-check { echo "Verifying commit: $(git rev-parse HEAD)" | gpg --batch --yes --local-user FD18D9D3B8C47685 --clearsign }


function SetGKECluster {
    param (
        [string]$PROJECT_ID,
        [string]$GKE_CLUSTER_NAME,
        [string]$GKE_NAMESPACE,
        [string]$REGION
    )

    $CMD_GCP_PROJECT_SET = "gcloud config set project $PROJECT_ID"
    $CMD_GCP_CLUSTER_SET = "gcloud container clusters get-credentials $GKE_CLUSTER_NAME --region $REGION --project $PROJECT_ID --internal-ip"
    $CMD_KCTL_NAMESPACE_SET = "kubectl config set-context gke_${PROJECT_ID}_${REGION}_${GKE_CLUSTER_NAME} --namespace=$GKE_NAMESPACE"

    $CMD_GCP_PROJECT_SET
    Invoke-Expression $CMD_GCP_PROJECT_SET

    $CMD_GCP_CLUSTER_SET
    Invoke-Expression $CMD_GCP_CLUSTER_SET

    $CMD_KCTL_NAMESPACE_SET
    Invoke-Expression $CMD_KCTL_NAMESPACE_SET

    kubectl config current-context
    gcloud config list
    kubectl get namespace
}

function GoodNight { Stop-Transcript -ErrorAction SilentlyContinue; start cmd -Arg "/c timeout /t 3 && get hibernate"; exit; }  Set-Alias gn GoodNight -Force
function hist { 
  $find = $args; 
  Write-Host "Finding in full history using {`$_ -like `"*$find*`"}"; 
  Get-Content (Get-PSReadlineOption).HistorySavePath | ? {$_ -like "*$find*"} | Get-Unique | more 
}

# Make sure you have fzf installed and in your PATH

# 1. Define your custom function
function Invoke-FzfHistory {
    # Get command history, pipe to fzf for interactive selection
    $command = $(history).CommandLine | fzf

    # If a command was selected (i.e., you didn't press Esc)
    if ($command) {
        # First, clear the current command line
        [Microsoft.PowerShell.PSConsoleReadLine]::RevertLine()
        
        # Then, put the selected command onto the command line
        [Microsoft.PowerShell.PSConsoleReadLine]::Insert($command)
    }
}

# 2. Bind the key to the SCRIPT BLOCK of your function
Set-PSReadLineKeyHandler -Key 'Ctrl+r' -ScriptBlock ${function:Invoke-FzfHistory}

# Optional but recommended: A version that executes immediately
# function Invoke-AndExecute-FzfHistory {
#     $command = $(history).CommandLine | fzf
#     if ($command) {
#         Invoke-Expression $command
#     }
# }
# Set-PSReadLineKeyHandler -Key 'Alt+r' -ScriptBlock ${function:Invoke-AndExecute-FzfHistory}

function javaapps { jps -mlvV }

function kai { kubectl-ai $args }

function l { DIR -Name }

function lr { DIR -Name -Recurse }

function lsd { dir | ? { $_.PSIsContainer } }

function lsl { dir | ? { !$_.PSIsContainer } }

function mcd { md $1; Push-Location $1; }

function mci() { echo "mvn clean install $args"; mvn clean install $args; if ($?) { get message "build successful at %TIME% for %CD%" } else { get message "build failed at %TIME% for %CD%"; } }

function mcist() { echo "mvn clean install -DskipTests $args"; mvn clean install -DskipTests $args; if ($?) { get message "build successful at %TIME% for %CD%" } else { get message "build failed at %TIME% for %CD%"; } }

function mcimts() { echo "mvn clean install -Dmaven.test.skip $args"; mvn clean install -Dmaven.test.skip $args; if ($?) { get message "build successful at %TIME% for %CD%" } else { get message "build failed at %TIME% for %CD%"; } }

function nano { wsl nano $args }

function npp { start-process notepad++.exe "$args" }

function pd { param($path = $args -join ' '); if ($path) { Push-Location -Path $path }; ls }

function po { Pop-Location; pd @args; ls; }

function restartrans { Stop-Transcript -ErrorAction SilentlyContinue; clear; Start-Transcript -Path $File -Append; }

function restartwsl {  wsl --shutdown; timeout /t 9 /nobreak; start wsl -Args "--cd $PWD" }

function startui { start "$PWD" /D "$PWD" /min cmd /k "npm start && call get max && PAUSE && exit" ; get min; }

function vars { Get-Variable | Where-Object { $_.Visibility -eq 'Public' } }

function tmpfile {
	echo `$null>"$TMPDR\$args";
	$null>"$TMPDR\$args";
	PAUSE
	echo "ampersand notepad++.exe $TMPDR\$args"
	& notepad++.exe "$TMPDR\$args"
	explorer "$TMPDR"
	get min
}

function vim { wsl vim $args }

function whichjava { java -version; javac -version; echo env:JAVA_HOME=$env:JAVA_HOME }

function whereis([string]$programname) { (Get-Command $programname).Path }

function wingrep([string]$somefile, [string]$expression){ 
	#get-content $ | where { $_ -match "$expression"}
	select-string $somefile -pattern "$expression"
}

function winsed([string]$somefile, [string]$expression, [string]$replace){
	get-content $somefile | %{$_ -replace "$expression","$replace"}
}

# Export all functions to make them available globally when module is imported with -Global
Export-ModuleMember -Function * -Alias * -Variable *