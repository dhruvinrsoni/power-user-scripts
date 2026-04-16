Write-Host "Running $($MyInvocation.MyCommand.Name)"
Write-Host "Path: $($MyInvocation.MyCommand.Path)"
# ─────────────────────────────────────────────────────────────────────────
#  powershell.ps1 — Power-user functions & aliases for PowerShell
#
#  LOADING STRATEGY:
#    This file is loaded via dot-sourcing (. $file) by LoadPowerShellDoskeys.
#    This keeps all functions in the caller's (global) scope so navigation
#    commands like pd, po, cdv, dirs share the same location stack that the
#    prompt reads.
#
#    (Renamed from .psm1 to .ps1 because Import-Module creates an isolated
#    "module session state" with a private location stack, and the .psm1
#    file association on Windows opens Notepad on every dot-source load.)
#
#    An Export-ModuleMember guard at the bottom is kept as a safety net in
#    case anyone ever Import-Module's this file directly.
# ─────────────────────────────────────────────────────────────────────────

function .. { cd '..' }

function ... { Set-Location '..\..' }

function a { type $DOSFILE_BASE; type $DOSFILE }

function b { 
	$argsString = $args -join ' '
    start cmd -Args "/c call get min && echo mvn clean install $argsString && call mvn clean install $argsString && get max && get message 'build successful at $TIME for $PWD' || get message 'build failed at $TIME for $PWD' & PAUSE" -WindowStyle Maximized 
}

function bye { Stop-Transcript -ErrorAction SilentlyContinue; exit; }  Set-Alias e bye -Force
function c { cls }

# Pop-Location then cdv — swap top of the location stack for a new project directory
function cdm { Pop-Location; cdv @args; ls; }

# Navigate to a named variable/env-var path via Push-Location (adds to the prompt's '+' stack)
function cdv {
    $path = (Get-Variable -Name $args[0] -Scope Global -ValueOnly -ErrorAction SilentlyContinue)
    if ($null -eq $path) { $path = [Environment]::GetEnvironmentVariable($args[0]) }
    if ($null -eq $path) { Write-Error "No variable or env var named '$($args[0])' found"; return }
    Push-Location -Path $path
    ls
}

function cmdmax { Start-Process cmd.exe -WindowStyle Maximized }

# Show full location stack: current dir + all pushed dirs (visible as '+' in the prompt)
function dirs { @( Get-Location ) + (Get-Location -Stack).ToArray() | Select-Object Path }

function echov($varName) {
    if ($varValue = (Get-Variable -Name $varName -Scope Global -ErrorAction SilentlyContinue).Value) {
        $varValue | Tee-Object -Variable _ | Set-Clipboard
    } else {
        Write-Error "Variable '$varName' does not exist."
    }
}

function ex(){ explorer ($args -join ' ') }

function exv(){
    $path = (Get-Variable -Name $args[0] -Scope Global -ValueOnly -ErrorAction SilentlyContinue)
    if ($null -eq $path) { $path = [Environment]::GetEnvironmentVariable($args[0]) }
    explorer ($path -join ' ')
}

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

function g { git @args }

function git-ls { Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\.git\\' } | ForEach-Object { $_.FullName.Replace('$PWD.Path', '') } }

#
# GPG Sanity Check Function
# This works because it runs the gpg command directly in PowerShell,
# where we know the gpg-agent is working correctly.
#
function gpg-check { echo "Verifying commit: $(git rev-parse HEAD)" | gpg --batch --yes --local-user FD18D9D3B8C47685 --clearsign }

# Seamless per-repo GitHub CLI authentication
function gh {
    # Check if the current git repo has a custom local gh token
    $localToken = git config --local gh.token 2>$null

    if (![string]::IsNullOrWhiteSpace($localToken)) {
        # Temporarily inject the local token into the environment
        $originalToken = $env:GH_TOKEN
        $env:GH_TOKEN = $localToken
        
        try {
            # Run the actual GitHub CLI command
            & gh.exe @args
        } finally {
            # Clean up immediately so it doesn't leak into other directories
            if ($originalToken) { $env:GH_TOKEN = $originalToken } 
            else { Remove-Item Env:\GH_TOKEN -ErrorAction SilentlyContinue }
        }
    } else {
        # No local token found, run normally using global auth
        & gh.exe @args
    }
}


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

# Create a directory and push into it (adds to the prompt's '+' stack)
function mcd { md $1; Push-Location $1; }

function mci() { echo "mvn clean install $args"; mvn clean install $args; if ($?) { get message "build successful at %TIME% for %CD%" } else { get message "build failed at %TIME% for %CD%"; } }

function mcist() { echo "mvn clean install -DskipTests $args"; mvn clean install -DskipTests $args; if ($?) { get message "build successful at %TIME% for %CD%" } else { get message "build failed at %TIME% for %CD%"; } }

function mcimts() { echo "mvn clean install -Dmaven.test.skip $args"; mvn clean install -Dmaven.test.skip $args; if ($?) { get message "build successful at %TIME% for %CD%" } else { get message "build failed at %TIME% for %CD%"; } }

function nano { wsl nano $args }

function npp { start-process notepad++.exe "$args" }

# Push-Location to a path, then list contents (each call adds one '+' to the prompt)
function pd { param($path = $args -join ' '); if ($path) { Push-Location -Path $path }; ls }

# Pop-Location (removes one '+' from the prompt), optionally push a new path
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
    Generates or executes commands to create symbolic links for all executables found in the system's PATH, consolidating them into a single directory.

.DESCRIPTION
    This function provides a robust solution for managing a crowded PATH environment variable.

    DEFAULT BEHAVIOR (Preview Mode):
    By default, this function performs a dry run. It scans the PATH, finds all unique executables, and prints the exact 'mklink' commands needed to create symbolic links for them in a target directory. This output can be inspected or redirected to a .bat file to be run later.

    EXECUTION MODE (-Execute switch):
    When the -Execute switch is used, the function will make actual changes to the system. It requires Administrator privileges, creates the target directory if needed, and then executes the 'mklink' commands to create the symbolic links.

.PARAMETER TargetPath
    The directory where the symbolic links will be created. Defaults to 'C:\tools'.

.PARAMETER ExcludePaths
    An array of full directory paths to exclude from scanning. This prevents clutter from standard system utilities. Defaults to common Windows and PowerShell directories.

.PARAMETER Execute
    A switch parameter that changes the function from a preview mode to an execution mode.
    *** WARNING: This switch will make changes to your file system. You must run PowerShell as an Administrator to use it. ***

.EXAMPLE
    PS C:\> Sync-PathToTools

    # Preview of commands to be generated. Run with -Execute switch to perform these actions.
    # To save this as a script, run: Sync-PathToTools > create_links.bat
    mklink "C:\tools\git.exe" "C:\Program Files\Git\cmd\git.exe"
    mklink "C:\tools\node.exe" "C:\Program Files\nodejs\node.exe"
    ...
    (This shows a preview of the links that would be created. No changes are made.)

.EXAMPLE
    PS C:\> Sync-PathToTools > create_my_links.bat
    (This saves all the generated 'mklink' commands into a batch file that you can review and run later.)

.EXAMPLE
    PS C:\> Sync-PathToTools -Execute

    [INFO] Administrator privileges confirmed.
    [INFO] Creating link: git.exe
    [INFO] Creating link: node.exe
    ...
    (This will actually create the symbolic links. Requires an elevated (Administrator) PowerShell session.)

.NOTES
    Author: Gemini Enterprise, refined with guidance from Dhruvin Soni.
    The -Execute switch requires PowerShell to be run as an Administrator.
#>
function Sync-PathToTools {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$TargetPath = 'C:\tools',

        [Parameter(Mandatory = $false)]
        [string[]]$ExcludePaths = @(
            "$env:SystemRoot",
            "$env:SystemRoot\System32",
            "$env:SystemRoot\System32\Wbem",
            "$env:SystemRoot\System32\WindowsPowerShell\v1.0"
        ),

        [Parameter(Mandatory = $false)]
        [switch]$Execute
    )

    # --- Core Logic to Find Executables (Used by both modes) ---

    $allExcludedPaths = $ExcludePaths + $TargetPath
    $scannablePaths = ($env:Path -split ';') | Where-Object { $_ -and -not [string]::IsNullOrWhiteSpace($_) } | Get-Unique | Where-Object {
        $currentPath = $_
        $isExcluded = $false
        foreach ($excluded in $allExcludedPaths) {
            # Use -replace to normalize path separators for a reliable comparison
            if (($currentPath -replace '\\', '/') -eq ($excluded -replace '\\', '/')) {
                $isExcluded = $true
                break
            }
        }
        -not $isExcluded
    }
    $executablesToLink = $scannablePaths | ForEach-Object {
        if (Test-Path $_) {
            Get-ChildItem -Path $_ -File -ErrorAction SilentlyContinue | Where-Object { ($env:PATHEXT -split ';') -contains $_.Extension }
        }
    } | Group-Object -Property Name | ForEach-Object { $_.Group[0] }

    # --- Mode Switching ---

    if ($Execute.IsPresent) {
        # --- EXECUTION MODE ---
        $currentUser = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
        if (-not $currentUser.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            throw "Execution requires Administrator privileges. Please re-run with the -Execute switch in a terminal opened as Administrator."
        }
        Write-Host "[INFO] Administrator privileges confirmed. Starting execution..." -ForegroundColor Green

        if (-not (Test-Path -Path $TargetPath)) {
            Write-Host "[INFO] Creating target directory at $TargetPath..." -ForegroundColor Yellow
            New-Item -Path $TargetPath -ItemType Directory | Out-Null
        }

        foreach ($exe in $executablesToLink) {
            $linkName = Join-Path -Path $TargetPath -ChildPath $exe.Name
            $targetName = $exe.FullName
            if (-not (Test-Path -Path $linkName)) {
                Write-Host "[INFO] Creating link: $($exe.Name)"
                cmd /c "mklink ""$linkName"" ""$targetName""" | Out-Null
            } else {
                Write-Host "[INFO] Link for $($exe.Name) already exists. Skipping." -ForegroundColor Gray
            }
        }
        Write-Host "[SUCCESS] Tool synchronization complete." -ForegroundColor Green

    } else {
        # --- PREVIEW / SCRIPT GENERATION MODE (DEFAULT) ---
        Write-Output "# Preview of commands to be generated. Run this function with the -Execute switch to perform these actions."
        Write-Output "# To save this as a script, run: Sync-PathToTools > create_links.bat"
        
        foreach ($exe in $executablesToLink) {
            $linkName = Join-Path -Path $TargetPath -ChildPath $exe.Name
            $targetName = $exe.FullName
            # Output the exact, executable command string
            Write-Output "mklink ""$linkName"" ""$targetName"""
        }
    }
}

# Guard: Export-ModuleMember is only meaningful inside a module context.
# When dot-sourced (our default path), $MyInvocation.MyCommand.ScriptBlock.Module
# is $null, so this block is skipped — not needed since all functions are
# already in the caller's (global) scope.
# When Import-Module'd, this ensures all functions/aliases/variables are
# properly exported from the module boundary.
if ($MyInvocation.MyCommand.ScriptBlock.Module) {
    Export-ModuleMember -Function * -Alias * -Variable *
}
