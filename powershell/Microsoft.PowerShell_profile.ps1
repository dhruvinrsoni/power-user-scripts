Write-Host "Running $($MyInvocation.MyCommand.Name) (Path: $($MyInvocation.MyCommand.Path))"
#$host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.size(158,32766)
try {
    $bufferwidth = $host.UI.RawUI.MaxPhysicalWindowSize.Width - 2
    $bufferheight = [Math]::Min(9999, $host.UI.RawUI.MaxPhysicalWindowSize.Height * 10)
    $host.UI.RawUI.BufferSize = New-Object System.Management.Automation.Host.Size($bufferwidth, $bufferheight)
} catch {
    Write-Host "BufferSize error: $_" -ForegroundColor Red
}
Import-Module "$env:ROOT\github\dhruvinrsoni\power-user-scripts\powershell\Modules\SetConsoleFont.psm1"

# Install-Module -Name PowerShellGet
# Install-Module -Name PSReadLine -Scope CurrentUser -Force -SkipPublisherCheck
# $FontFile="$env:ROOT\github\dhruvinrsoni\power-user-scripts\powershell\JetBrains Mono Regular Nerd Font Complete Windows Compatible.ttf"
# if(Test-Path "$FontFile"){
	# echo "Running $FontFile"
	# Set-ConsoleFont "$FontFile"
# }

#f45873b3-b655-43a6-b217-97c00aa0db58 PowerToys CommandNotFound module
Import-Module -Name Microsoft.WinGet.CommandNotFound
$PROFILE | Format-List -Force

<# function prompt
{
    Write-Host ("PS " + $(get-date) + " " + $(pwd) +">") -nonewline -foregroundcolor White
    return " "
}
function prompt {
    $dateTime = get-date -Format "dd.MM.yyyy HH:mm:ss"
    $currentDirectory = $(Get-Location)
    $UncRoot = $currentDirectory.Drive.DisplayRoot

    write-host "$dateTime" -NoNewline -ForegroundColor White
    write-host " $UncRoot" -ForegroundColor Gray
    # Convert-Path needed for pure UNC-locations
    write-host "PS $(Convert-Path $currentDirectory)>" -NoNewline -ForegroundColor Yellow
    return " "
} #>

# Dot-source function libraries directly at profile scope (not inside a function).
#
# WHY NOT A FUNCTION: Dot-sourcing inside a function creates definitions in
# the function's local scope. When the function returns, all definitions are
# lost. There is no -Global flag for dot-sourcing like Import-Module has.
#
# WHY NOT Import-Module: Import-Module creates an isolated "module session
# state" with its own private location stack. Functions like pd, po, cdv,
# dirs that call Push-Location / Pop-Location would push onto the module's
# private stack instead of the global one, making them invisible to the
# prompt's '+' depth indicators.
#
# By dot-sourcing here at profile scope (which is global scope via the
# dot-source loading chain), all functions land in the global scope and
# persist for the entire session, sharing the same location stack as the prompt.
#
# Load order: OneDrive baseline first, repo overrides second (repo wins).
. "$DOSFILE"        # OneDrive baseline (common/work-specific functions)
. "$DOSFILE_BASE"   # Repo overrides (power-user-scripts — wins on conflicts)

function Reload-Profile {
	Stop-Transcript;
	$env:HOME=""
	Remove-Item Env:HOME
    @(
        $Profile.AllUsersAllHosts,
        $Profile.AllUsersCurrentHost,
        $Profile.CurrentUserAllHosts,
        $Profile.CurrentUserCurrentHost
    ) | % {
        if(Test-Path $_){
            Write-Verbose "Running $_"
            . $_
        }
    }    
} Set-Alias reload Reload-Profile -Force

function starttrans() { Start-Transcript -Path $TranscriptLogFileName -Append; }

function stoptrans() { Stop-Transcript; }

function phoenix(){ 
	$env:HOME=""
	Remove-Item Env:HOME
	if ($PSVersionTable.PSVersion.Major -eq '5') {
		Start-Process powershell; 
	} else {
		Start-Process pwsh; 
	}
	# Start-Process powershell; 
	Stop-Transcript; 
	exit; 
}

# Import the Chocolatey Profile that contains the necessary code to enable
# tab-completions to function for `choco`.
# Be aware that if you are missing these lines from your profile, tab completion
# for `choco` will not function.
# See https://ch0.co/tab-completion for details.
$ChocolateyProfile = "$env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
if (Test-Path($ChocolateyProfile)) {
  Import-Module "$ChocolateyProfile"
}

#To run copilot -p "List my open PRs" --allow-all-tools
#https://teams.microsoft.com/l/message/19:h9y5DglJJEeyLLaEB88IWHvkhaUfzCTFbKjgMRdlsnE1@thread.tacv2/1761244086645?tenantId=4d3d260a-9c40-4306-8dac-0d64717039ec&groupId=7ff56601-6dea-46f5-bddc-2deebb1a1495&parentMessageId=1760630107376&teamName=GitHub%20Copilot%20Users&channelName=GitHub%20Copilot%20User%20Community&createdTime=1761244086645
# $env:NODE_TLS_REJECT_UNAUTHORIZED = "0"
#Below is permeanent fix
# Get-ChildItem -Path Cert:\LocalMachine\Root | Where-Object { $_.Subject -like "*Zscaler*" }

if ($env:TERM_PROGRAM -eq "vscode") { . "$(code --locate-shell-integration-path pwsh)" }
