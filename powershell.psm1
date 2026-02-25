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

function envexts { > $executableExtensions = $env:PATHEXT -split ';'; ($env:Path -split ';') | ForEach-Object { if (Test-Path $_) { Get-ChildItem -Path $_ -File -ErrorAction SilentlyContinue | Where-Object { $executableExtensions -contains $_.Extension } } } | Select-Object FullName }

<#
.SYNOPSIS
    Scans the user's PATH environment variable and creates symbolic links for all found executables in a single, consolidated directory.

.DESCRIPTION
    This function automates the process of managing a crowded PATH variable. It finds all unique executables (.exe, .cmd, etc.) in the directories listed in $env:Path, excluding common system directories. It then creates symbolic links for these executables in a specified target directory (default C:\tools).

    This allows you to replace many entries in your PATH with a single one, preventing you from hitting the 2,047 character limit.

    The function includes a -WhatIf switch for a safe preview and requires Administrator privileges to run.

.PARAMETER TargetPath
    The directory where the symbolic links will be created. This folder will be created if it doesn't exist.
    Defaults to 'C:\tools'.

.PARAMETER ExcludePaths
    An array of full directory paths to exclude from scanning. This is used to prevent clutter from standard system utilities.
    Defaults to common Windows and PowerShell directories.

.PARAMETER WhatIf
    A switch parameter that shows what links would be created without actually creating them. Use this for a safe preview.

.EXAMPLE
    PS C:\> Sync-PathToTools -WhatIf

    What if: Performing the operation "Create Symbolic Link" on target "C:\tools\git.exe -> C:\Program Files\Git\cmd\git.exe".
    What if: Performing the operation "Create Symbolic Link" on target "C:\tools\node.exe -> C:\Program Files\nodejs\node.exe".
    (This shows a preview of the links that would be created.)

.EXAMPLE
    PS C:\> Sync-PathToTools

    [INFO] Administrator privileges confirmed.
    [INFO] Creating target directory at C:\tools...
    [INFO] Creating link: C:\tools\git.exe -> C:\Program Files\Git\cmd\git.exe
    (This will actually create the symbolic links. Run PowerShell as Administrator.)

.NOTES
    Author: Gemini Enterprise, based on collaboration with Dhruvin Soni.
    Requires: PowerShell to be run as an Administrator to create symbolic links.
#>
function Sync-PathToTools {
    [CmdletBinding(SupportsShouldProcess = $true)]
    param(
        [Parameter(Mandatory = $false)]
        [string]$TargetPath = 'C:\tools',

        [Parameter(Mandatory = $false)]
        [string[]]$ExcludePaths = @(
            "$env:SystemRoot",
            "$env:SystemRoot\System32",
            "$env:SystemRoot\System32\wbem",
            "$env:SystemRoot\System32\WindowsPowerShell\v1.0"
        )
    )

    # --- Pre-flight Checks & Setup ---

    # 1. Administrator Check
    $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        throw "This script requires Administrator privileges to create symbolic links. Please re-run from a terminal opened as Administrator."
    }
    Write-Host "[INFO] Administrator privileges confirmed." -ForegroundColor Green

    # 2. Create Target Directory if it doesn't exist
    if (-not (Test-Path -Path $TargetPath)) {
        if ($PSCmdlet.ShouldProcess($TargetPath, "Create Directory")) {
            Write-Host "[INFO] Creating target directory at $TargetPath..." -ForegroundColor Yellow
            New-Item -Path $TargetPath -ItemType Directory | Out-Null
        }
    }

    # 3. Dynamically add the TargetPath to the exclusion list to prevent self-scanning
    $allExcludedPaths = $ExcludePaths + $TargetPath

    # --- Core Logic ---

    # Get all unique, non-excluded paths from the $env:Path
    $scannablePaths = ($env:Path -split ';') | Where-Object { $_ -and -not [string]::IsNullOrWhiteSpace($_) } | Get-Unique | Where-Object {
        $currentPath = $_
        $isExcluded = $false
        foreach ($excluded in $allExcludedPaths) {
            if ($currentPath -eq $excluded) {
                $isExcluded = $true
                break
            }
        }
        -not $isExcluded
    }

    # Find all executables, group by name to handle duplicates, and select the first one found (mimicking PATH behavior)
    $executablesToLink = $scannablePaths | ForEach-Object {
        if (Test-Path $_) {
            Get-ChildItem -Path $_ -File -ErrorAction SilentlyContinue | Where-Object { ($env:PATHEXT -split ';') -contains $_.Extension }
        }
    } | Group-Object -Property Name | ForEach-Object { $_.Group[0] }

    Write-Host "[INFO] Found $($executablesToLink.Count) unique executables to process." -ForegroundColor Cyan

    # --- Execution Logic ---

    foreach ($exe in $executablesToLink) {
        $linkName = Join-Path -Path $TargetPath -ChildPath $exe.Name
        $targetName = $exe.FullName
        $actionMessage = "Create Symbolic Link: $linkName -> $targetName"

        if ($PSCmdlet.ShouldProcess($targetName, $actionMessage)) {
            # Only create the link if it doesn't already exist.
            if (-not (Test-Path -Path $linkName)) {
                Write-Host "[INFO] Creating link: $($exe.Name)"
                # We must use cmd /c for the 'mklink' internal command
                cmd /c "mklink ""$linkName"" ""$targetName""" | Out-Null
            }
            else {
                Write-Host "[INFO] Link for $($exe.Name) already exists. Skipping." -ForegroundColor Gray
            }
        }
    }

    Write-Host "[SUCCESS] Tool synchronization complete." -ForegroundColor Green
}


# Export all functions to make them available globally when module is imported with -Global
Export-ModuleMember -Function * -Alias * -Variable *