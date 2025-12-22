powershell -noprofile -Window Maximized -Command "exit"
#powershell -noprofile -Window Minimized -Command "exit"

######## POSH-GIT

#$path = Get-Location
#$scriptName = $MyInvocation.MyCommand.Name
#$completeScript = $path\$scriptName
#echo Current User and All Shells - $completeScript
#echo "Current User and All Shells - $profile"
if ($PSCommandPath -eq $null) { 
	function GetPSCommandPath() {
		return $MyInvocation.PSCommandPath; 
	} 
	$PSCommandPath = GetPSCommandPath; 
}
#echo "Current User and All Shells -           $PSCommandPath"
$myprofile=$PSCommandPath

# ... Import-Module for posh-git here ...
Import-Module posh-git
# Background colors

# $GitPromptSettings.AfterStash.BackgroundColor = 0x3465A4
# $GitPromptSettings.AfterStatus.BackgroundColor = 0x3465A4
# $GitPromptSettings.BeforeIndex.BackgroundColor = 0x3465A4
# $GitPromptSettings.BeforeStash.BackgroundColor = 0x3465A4
# $GitPromptSettings.BeforeStatus.BackgroundColor = 0x3465A4
# $GitPromptSettings.BranchAheadStatusSymbol.BackgroundColor = 0x3465A4
# $GitPromptSettings.BranchBehindAndAheadStatusSymbol.BackgroundColor = 0x3465A4
# $GitPromptSettings.BranchBehindStatusSymbol.BackgroundColor = 0x3465A4
# $GitPromptSettings.BranchColor.BackgroundColor = 0x3465A4
# $GitPromptSettings.BranchGoneStatusSymbol.BackgroundColor = 0x3465A4
# $GitPromptSettings.BranchIdenticalStatusSymbol.BackgroundColor = 0x3465A4
# $GitPromptSettings.DefaultColor.BackgroundColor = 0x3465A4
# $GitPromptSettings.DelimStatus.BackgroundColor = 0x3465A4
# $GitPromptSettings.ErrorColor.BackgroundColor = 0x3465A4
# $GitPromptSettings.IndexColor.BackgroundColor = 0x3465A4
# $GitPromptSettings.LocalDefaultStatusSymbol.BackgroundColor = 0x3465A4
# $GitPromptSettings.LocalStagedStatusSymbol.BackgroundColor = 0x3465A4
# $GitPromptSettings.LocalWorkingStatusSymbol.BackgroundColor = 0x3465A4
# $GitPromptSettings.StashColor.BackgroundColor = 0x3465A4
$GitPromptSettings.WorkingColor.BackgroundColor = 0x005faf
$GitPromptSettings.AfterStash.BackgroundColor = 0x005faf
$GitPromptSettings.AfterStatus.BackgroundColor = 0x005faf
$GitPromptSettings.BeforeIndex.BackgroundColor = 0x005faf
$GitPromptSettings.BeforeStash.BackgroundColor = 0x005faf
$GitPromptSettings.BeforeStatus.BackgroundColor = 0x005faf
$GitPromptSettings.BranchAheadStatusSymbol.BackgroundColor = 0x005faf
$GitPromptSettings.BranchBehindAndAheadStatusSymbol.BackgroundColor = 0x005faf
$GitPromptSettings.BranchBehindStatusSymbol.BackgroundColor = 0x005faf
$GitPromptSettings.BranchColor.BackgroundColor = 0x005faf
$GitPromptSettings.BranchGoneStatusSymbol.BackgroundColor = 0x005faf
$GitPromptSettings.BranchIdenticalStatusSymbol.BackgroundColor = 0x005faf
$GitPromptSettings.DefaultColor.BackgroundColor = 0x005faf
$GitPromptSettings.DelimStatus.BackgroundColor = 0x005faf
$GitPromptSettings.ErrorColor.BackgroundColor = 0x005faf
$GitPromptSettings.IndexColor.BackgroundColor = 0x005faf
$GitPromptSettings.LocalDefaultStatusSymbol.BackgroundColor = 0x005faf
$GitPromptSettings.LocalStagedStatusSymbol.BackgroundColor = 0x005faf
$GitPromptSettings.LocalWorkingStatusSymbol.BackgroundColor = 0x005faf
$GitPromptSettings.StashColor.BackgroundColor = 0x005faf
$GitPromptSettings.WorkingColor.BackgroundColor = 0x005faf

# Foreground colors

$GitPromptSettings.AfterStash.ForegroundColor = 0xF49797
$GitPromptSettings.AfterStatus.ForegroundColor = 0x729FCF
$GitPromptSettings.BeforeStash.ForegroundColor = 0xF49797
#$GitPromptSettings.BeforeStatus.ForegroundColor = 0x729FCF
$GitPromptSettings.BeforeStatus.ForegroundColor = 0x87d700
$GitPromptSettings.BranchAheadStatusSymbol.ForegroundColor = 0x8AE234
$GitPromptSettings.BranchBehindAndAheadStatusSymbol.ForegroundColor = 0xFCE94F
$GitPromptSettings.BranchBehindStatusSymbol.ForegroundColor = 0xF49797
$GitPromptSettings.BranchColor.ForegroundColor = 0xFBFBFB
$GitPromptSettings.BranchGoneStatusSymbol.ForegroundColor = 0x729FCF
$GitPromptSettings.BranchIdenticalStatusSymbol.ForegroundColor = 0x729FCF
$GitPromptSettings.DefaultColor.ForegroundColor = 0xB5BBAE
$GitPromptSettings.DelimStatus.ForegroundColor = 0x729FCF
$GitPromptSettings.ErrorColor.ForegroundColor = 0xF49797
$GitPromptSettings.IndexColor.ForegroundColor = 0x2EC3C3
$GitPromptSettings.StashColor.ForegroundColor = 0xF49797
$GitPromptSettings.WorkingColor.ForegroundColor = 0xFCE94F

# Prompt shape

$GitPromptSettings.AfterStatus.Text = " "
$GitPromptSettings.BeforeStatus.Text = "  "
$GitPromptSettings.BranchAheadStatusSymbol.Text = ""
$GitPromptSettings.BranchBehindStatusSymbol.Text = ""
$GitPromptSettings.BranchGoneStatusSymbol.Text = ""
$GitPromptSettings.BranchBehindAndAheadStatusSymbol.Text = ""
$GitPromptSettings.BranchIdenticalStatusSymbol.Text = ""
$GitPromptSettings.BranchUntrackedText = ""
$GitPromptSettings.DelimStatus.Text = " ॥"
$GitPromptSettings.LocalStagedStatusSymbol.Text = ""
$GitPromptSettings.LocalWorkingStatusSymbol.Text = ""

$GitPromptSettings.EnableStashStatus = $true
$GitPromptSettings.ShowStatusWhenZero = $true

######## INI FILE PARSER

function parseIniFile {
    [CmdletBinding()]
    param(
        [Parameter(Position = 0)]
        [String] $Inputfile
    )

    if ($Inputfile -eq "") {
        Write-Error "Ini File Parser: No file specified or selected to parse."
        Break
    }
    else {

        $ContentFile = Get-Content $Inputfile
        # commented Section
        $COMMENT_CHARACTERS = ";"
        # match section header
        $HEADER_REGEX = "\[+[A-Z0-9._ %<>/#+-]+\]"

        $OccurenceOfComment = 0
        $ContentComment = $ContentFile | Where-Object { ($_ -match "^\s*$COMMENT_CHARACTERS") -or ($_ -match "^$COMMENT_CHARACTERS") } | % {
            [PSCustomObject]@{ Comment = $_ ;
                Index                  = [Array]::IndexOf($ContentFile, $_)
            }
            $OccurenceOfComment++
        }

        $COMMENT_INI = @()
        foreach ($COMMENT_ELEMENT in $ContentComment) {
            $COMMENT_OBJ = New-Object PSObject
            $COMMENT_OBJ | Add-Member  -type NoteProperty -name Index -value $COMMENT_ELEMENT.Index
            $COMMENT_OBJ | Add-Member  -type NoteProperty -name Comment -value $COMMENT_ELEMENT.Comment
            $COMMENT_INI += $COMMENT_OBJ
        }

        $CONTENT_USEFUL = $ContentFile | Where-Object { ($_ -notmatch "^\s*$COMMENT_CHARACTERS") -or ($_ -notmatch "^$COMMENT_CHARACTERS") }
        $ALL_SECTION_HASHTABLE = $CONTENT_USEFUL | Where-Object { $_ -match $HEADER_REGEX } | % { [PSCustomObject]@{ Section = $_ ; Index = [Array]::IndexOf($CONTENT_USEFUL, $_) } }
        #$ContentUncomment | Select-String -AllMatches $HEADER_REGEX | Select-Object -ExpandProperty Matches

        $SECTION_INI = @()
        foreach ($SECTION_ELEMENT in $ALL_SECTION_HASHTABLE) {
            $SECTION_OBJ = New-Object PSObject
            $SECTION_OBJ | Add-Member  -type NoteProperty -name Index -value $SECTION_ELEMENT.Index
            $SECTION_OBJ | Add-Member  -type NoteProperty -name Section -value $SECTION_ELEMENT.Section
            $SECTION_INI += $SECTION_OBJ
        }

        $INI_FILE_CONTENT = @()
        $NBR_OF_SECTION = $SECTION_INI.count
        $NBR_MAX_LINE = $CONTENT_USEFUL.count

        #*********************************************
        # select each lines and value of each section
        #*********************************************
        for ($i = 1; $i -le $NBR_OF_SECTION ; $i++) {
            if ($i -ne $NBR_OF_SECTION) {
                if (($SECTION_INI[$i - 1].Index + 1) -eq ($SECTION_INI[$i].Index )) {
                    $CONVERTED_OBJ = @() #There is nothing between the two section
                }
                else {
                    $SECTION_STRING = $CONTENT_USEFUL | Select-Object -Index  (($SECTION_INI[$i - 1].Index + 1)..($SECTION_INI[$i].Index - 1)) | Out-String
                    $CONVERTED_OBJ = convertfrom-stringdata -stringdata $SECTION_STRING
                }
            }
            else {
                if (($SECTION_INI[$i - 1].Index + 1) -eq $NBR_MAX_LINE) {
                    $CONVERTED_OBJ = @() #There is nothing between the two section
                }
                else {
                    $SECTION_STRING = $CONTENT_USEFUL | Select-Object -Index  (($SECTION_INI[$i - 1].Index + 1)..($NBR_MAX_LINE - 1)) | Out-String
                    $CONVERTED_OBJ = convertfrom-stringdata -stringdata $SECTION_STRING
                }
            }
            $CURRENT_SECTION = New-Object PSObject
            $CURRENT_SECTION | Add-Member -Type NoteProperty -Name Section -Value $SECTION_INI[$i - 1].Section
            $CURRENT_SECTION | Add-Member -Type NoteProperty -Name Content -Value $CONVERTED_OBJ
            $INI_FILE_CONTENT += $CURRENT_SECTION
        }

        return $INI_FILE_CONTENT
    }
}

######## PROMPT


	
$CloudDevOpsMode=0;
$DevMode=1;
# do {
	# $msg = 'Engage and Patch the Cloud DevOps Kraken?' 
	# $response = Read-Host -Prompt $msg
	# if ($response -eq 'y') {
		# $CloudDevOpsMode=1
	# }
	# elseif ($response -eq 'n') {
		# $CloudDevOpsMode=0
	# }
	# else {
		# Write-Host "Invalid input or no response. Defaulting to 'No'."
		# $response='n'
		# $CloudDevOpsMode=0
	# }
# } until ($response -eq 'n' -Or $response -eq 'y')

# do {
    # $msg = 'Unleash the Debugging Dragon for DevMode Secrets?'
    # $response = Read-Host -Prompt $msg
    # if ($response -eq 'y') {
        # $DevMode=1
        # Write-Host "The Dragon roars! Revealing DevMode secrets..."
    # }
    # elseif ($response -eq 'n') {
        # $DevMode=0
        # Write-Host "The Dragon slumbers. Proceeding without its wisdom."
    # }
    # else {
        # Write-Host "The Dragon is perplexed. Defaulting to 'No'."
        # $response='n'
        # $DevMode=0
    # }
# } until ($response -eq 'n' -or $response -eq 'y')



# function Read-HostWithTimeout {
    # param (
        # [string]$Prompt,
        # [int]$TimeoutSeconds
    # )

    # $timeout = New-TimeSpan -Seconds $TimeoutSeconds
    # $endTime = (Get-Date).Add($timeout)

    # do {
        # $response = $(Write-Host; Write-Host $Prompt -ForegroundColor Green -BackgroundColor Black; Read-Host)
        # if ($response -ne '') {
            # break
        # }
    # } while ((Get-Date) -lt $endTime)

    # if ($response -eq '') {
        # # Write-Host; Write-Host -back Black -fore Red "No response received. Defaulting to 'No'."
        # # $response = 'n'
		# Write-Host; Write-Host -BackgroundColor Black -ForegroundColor Yellow "No response received. Marking as 'no input'."
        # $response = $null # Use $null to signify no input
    # }

    # return $response
# }
function Read-HostWithTimeout {
    param (
        [string]$Prompt,
        [int]$TimeoutSeconds
    )

    $timeout = New-TimeSpan -Seconds $TimeoutSeconds
    $response = '' # Initialize response

    # Display the prompt
    Write-Host
    Write-Host $Prompt -ForegroundColor Green -BackgroundColor Black

    # Wait for user input with a timeout
    $timer = [System.Diagnostics.Stopwatch]::StartNew()
    while ($timer.Elapsed -lt $timeout) {
        if ($Host.UI.RawUI.KeyAvailable) {
            $key = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
            $char = [string]::new($key.Character).ToLower() # Convert to string and lowercase
            if ($char -eq 'y' -or $char -eq 'n') {
                $response = $char
                break
            }
            if ($key.VirtualKeyCode -eq 13) { # Enter key
                break
            }
        }
        Start-Sleep -Milliseconds 100 # Small delay to prevent high CPU usage
    }
    $timer.Stop()

    # Trim and evaluate the response
    $response = $response.Trim()

    if ([string]::IsNullOrWhiteSpace($response)) {
        Write-Host
        Write-Host -BackgroundColor Black -ForegroundColor Yellow "No response received. Marking as 'no input'."
        $response = $null # Use $null to signify no input
    } elseif ($response -match '^[YyNn]$') {
        return $response.ToLower() # Return lowercase for consistency
    } else {
        Write-Host
        Write-Host -BackgroundColor Black -ForegroundColor Yellow "Invalid input. Marking as 'no input'."
        $response = $null # Use $null to signify no valid input
    }

    return $response
}

function resetprompt {
    $msg = "#=================================================#`n#>>> Engage and Patch the Cloud DevOps Kraken? <<<#`n#=================================================# "
    $userResponse = Read-HostWithTimeout -Prompt $msg -TimeoutSeconds 6
    Write-Host
    if ($userResponse -eq 'y') { 
        Write-Host -ForegroundColor Green -BackgroundColor Black "<===== [ Directive Confirmed: DevOps Mode ENGAGED. Awakened Kraken in Action! ] =====>"
        $script:CloudDevOpsMode = 1 
    } elseif ($userResponse -eq 'n') { 
        Write-Host -ForegroundColor Red -BackgroundColor Black "===> [ Action Canceled: DevOps Mode INACTIVE. Kraken in Standby. ] <==="
        $script:CloudDevOpsMode = 0 
    } else { 
        Write-Host -ForegroundColor Yellow -BackgroundColor Black "===> [ Unclear Command: DevOps Mode NOT ACTIVATED. Defaulting to Standby. ] <==="
        $script:CloudDevOpsMode = 0 
    }
    Write-Host

    $msg = "#=========================================================#`n#>>> Unleash the Debugging Dragon for DevMode Secrets? <<<#`n#=========================================================# "
    $userResponse = Read-HostWithTimeout -Prompt $msg -TimeoutSeconds 6
    Write-Host
    if ($userResponse -eq 'y') { 
        Write-Host -ForegroundColor Green -BackgroundColor Black "<===== [ The Dragon roars! Revealing DevMode secrets... ] =====>"
        $script:DevMode = 1 
    } elseif ($userResponse -eq 'n') { 
        Write-Host -ForegroundColor Red -BackgroundColor Black "===> [ The Dragon slumbers. Proceeding without its wisdom. ] <==="
        $script:DevMode = 0 
    } else { 
        Write-Host -ForegroundColor Yellow -BackgroundColor Black "===> [ The Dragon is perplexed. Defaulting to 'No'. ] <==="
        $script:DevMode = 0 
    }
    Write-Host
}

# Key Improvements:
# - Ensure $response is initialized to an empty string at the start of Read-HostWithTimeout
# - Ensure $timer is properly stopped and not reused across calls
# - Ensure $userResponse is correctly captured and reset in resetprompt


function Test-StandaloneWindow {
    # Load the necessary .NET assembly
    Add-Type -AssemblyName System.Diagnostics.Process

    # Get the current process
    $currentProcess = [System.Diagnostics.Process]::GetCurrentProcess()

    # Get the parent process ID
    $parentProcessId = $currentProcess.Parent.Id

    # Initialize the result object
    $result = [PSCustomObject]@{
        IsStandaloneWindow = $false
        ParentProcessId    = $parentProcessId
        ParentProcessName  = "Unknown"
        CurrentProcessId   = $currentProcess.Id
        CurrentProcessName = $currentProcess.ProcessName
    }

    # Try to get the parent process name
    try {
        $parentProcess = [System.Diagnostics.Process]::GetProcessById($parentProcessId)
        $result.ParentProcessName = $parentProcess.ProcessName
    } catch {
        $result.ParentProcessName = "Unknown"
    }

    # Check if the parent process is Idle
    if ($result.ParentProcessName -eq 'Idle' -or $result.ParentProcessName -eq 'powershell' -or $result.ParentProcessName -eq 'pwsh' -or $result.ParentProcessName -eq 'explorer') {
        $result.IsStandaloneWindow = $true
    }

    # Print debug information
    Write-Output "Debug Information:"
    Write-Output "-------------------"
    Write-Output "Current Process: $($result.CurrentProcessName)($($result.CurrentProcessId))"
    Write-Output "Parent Process: $($result.ParentProcessName)($($result.ParentProcessId))"
    Write-Output "Is Standalone Window: $($result.IsStandaloneWindow)"

    # Return the result object
    return $result
}

$result = Test-StandaloneWindow
# Use the output in other places
if ($result.IsStandaloneWindow) {
    Write-Output "This is a standalone window. Resetting the prompt for CloudDevOpsMode & DevMode..."
	# resetprompt
} else {
	Write-Output "This is not a standalone window. Cannot reset the prompt for CloudDevOpsMode & DevMode"
}
# Access debug information
$result | Format-List


set-content Function:prompt {
    # Start with a blank line, for breathing room :)
    Write-Host ""

    # Reset the foreground color to default
    $Host.UI.RawUI.ForegroundColor = "Gray"
    
    Write-Host "" -NoNewLine
    #Write-Host "$([char]27)[48;5;227;48;5;28m " -NoNewLine
    $NextForegroundColor = "5"
    $BackgroundColor = $((get-host).ui.rawui.BackgroundColor)

    # Write ERR for any PowerShell errors
    if ($Error.Count -ne 0) {
        Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;131m " -NoNewline
        $NextForegroundColor=0
        Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;131m  ERR $([char]27)[0m" -NoNewLine
        $NextForegroundColor = "131"
        $Error.Clear()
    }

    # Write non-zero exit code from last launched process
    if ($LASTEXITCODE -ne "") {
        Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;131m  $LASTEXITCODE $([char]27)[0m" -NoNewLine
        $NextForegroundColor = "131"
        $LASTEXITCODE = ""
    }

    # Write any custom prompt environment (f.e., from vs2019.ps1)
    # if (get-content variable:\PromptEnvironment -ErrorAction Ignore) {
        # Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;183m $([char]27)[38;5;54;48;5;183m$PromptEnvironment $([char]27)[0m" -NoNewLine
        # $NextForegroundColor = "183"
    # }

    # Write .NET SDK version
    <#if ($null -ne (Get-Command "dotnet" -ErrorAction Ignore)) {
        $dotNetVersion = (& dotnet --version)
        Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;54m $([char]27)[38;5;254m  $dotNetVersion $([char]27)[0m" -NoNewLine
        $NextForegroundColor = "54"
    }#>

	if($CloudDevOpsMode -eq 1)
	{
		# Write the current gcp project@account
		if ($null -ne (Get-Command "gcloud" -ErrorAction Ignore)) {
			$setProject = (& gcloud config list --format 'value(core.project)' 2> $null)
			if ($Error.Count -eq 0) {
				Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;239m $([char]27)[38;5;112m  $([char]27)[38;5;254m$setProject" -NoNewLine
				$NextForegroundColor = "239"
			}
			else {
				$Error.Clear()
			}
		}
		# if ($null -ne (Get-Command "gcloud" -ErrorAction Ignore)) {
			# $setAccount = (& gcloud config list --format 'value(core.account)' 2> $null)
			# if ($Error.Count -eq 0) {
				# Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;239m $([char]27)[38;5;112m $([char]27)[38;5;254m$setAccount" -NoNewLine
				# $NextForegroundColor = "239"
			# }
			# else {
				# $Error.Clear()
			# }
		# }
		
		# Write the current kubectl context
		if ($null -ne (Get-Command "kubectl" -ErrorAction Ignore)) {
			$currentContext = (& kubectl config current-context 2> $null)
			if ($Error.Count -eq 0) {
				Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;242m $([char]27)[38;5;112m  $([char]27)[38;5;254m$currentContext$([char]27)[0m" -NoNewLine
				$NextForegroundColor = "242"
			}
			else {
				$Error.Clear()
			}
		}

		# Write the current kubectl namespace
		if ($null -ne (Get-Command "kubens" -ErrorAction Ignore)) {
			$currentNamespace = (& kubens --current 2> $null)
			if ($Error.Count -eq 0) {
				# Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;239m $([char]27)[38;5;112m  $([char]27)[38;5;254m$currentNamespace $([char]27)[38;5;239;48;5;17m $([char]27)[0m" -NoNewLine
				Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;239m $([char]27)[38;5;112m  $([char]27)[38;5;254m$currentNamespace $([char]27)[38;5;239;48;5;5m $([char]27)[0m" -NoNewLine
				$NextForegroundColor = "239"
			}
			else {
				$Error.Clear()
			}
		} elseif ($null -ne (Get-Command "kubectl" -ErrorAction Ignore)) {
			$currentNamespace = (& kubectl config view --minify -o jsonpath='{..namespace}' 2> $null)
			if ($Error.Count -eq 0) {
				Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;239m $([char]27)[38;5;112m  $([char]27)[38;5;254m$currentNamespace$([char]27)[0m" -NoNewLine; $NextForegroundColor = "239"
				#Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;239m $([char]27)[38;5;112m  $([char]27)[38;5;254m$currentNamespace $([char]27)[38;5;239;48;5;5m "; $NextForegroundColor = "5"
			}
			else {
				$Error.Clear()
			}
		}

		# Write the current public cloud Azure CLI subscription
		# NOTE: You will need sed from somewhere (for example, from Git for Windows)
		# if (Test-Path ~/.azure/clouds.config) {
			# $cloudsConfig = parseIniFile ~/.azure/clouds.config
			# $azureCloud = $cloudsConfig | Where-Object { $_.Section -eq "[AzureCloud]" }
			# if ($null -ne $azureCloud) {
				# $currentSub = $azureCloud.Content.subscription
				# if ($null -ne $currentSub) {
					# $currentAccount = (Get-Content ~/.azure/azureProfile.json | ConvertFrom-Json).subscriptions | Where-Object { $_.id -eq $currentSub }
					# if ($null -ne $currentAccount) {
						# #Write-Host " $([char]27)[38;5;$($NextForegroundColor);48;5;30m  $([char]27)[38;5;254m$($currentAccount.name) $([char]27)[0m" -NoNewLine
						# Write-Host " $([char]27)[38;5;$($NextForegroundColor);48;5;30m  $([char]27)[38;5;254m$($currentAccount.name) $([char]27)[0m"
							# $NextForegroundColor = "30"
					# }
				# }
			# }
		# }

		# # Write the current Git information
		# if ($null -ne (Get-Command "Get-GitDirectory" -ErrorAction Ignore)) {
			# if (Get-GitDirectory -ne $null) {
				# #$GitPromptSettings.PathStatusSeparator = "$([char]27)[38;5;$($NextForegroundColor);48;5;25m $([char]27)[38;5;112m  "
				# $GitPromptSettings.PathStatusSeparator = "$([char]27)[38;5;$($NextForegroundColor);48;5;25m $([char]27)[38;5;112m  "
				# Write-Host (Write-VcsStatus) -NoNewLine
				# $NextForegroundColor = "25"
			# }
		# }
	}
    # Write the current directory, with home folder normalized to ~
    $currentPath = (get-location).Path.replace($home, "~")
    $idx = $currentPath.IndexOf("::")
    if ($idx -gt -1) { $currentPath = $currentPath.Substring($idx + 2) }
    $host.UI.RawUI.WindowTitle=$currentPath

    # Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;28m $([char]27)[38;5;227;48;5;28m  $([char]27)[38;5;254m$currentPath$([char]27)[0m" -NoNewline
    # Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;28m $([char]27)[38;5;227;48;5;28m  $([char]27)[38;5;254m$currentPath" -NoNewLine; $NextForegroundColor = "28"

	# Write-Host "$([char]27)[38;5;$($NextForegroundColor);48;5;5m $([char]27)[0m " -NoNewLine

    # Reset LASTEXITCODE so we don't show it over and over again
    $global:LASTEXITCODE = 0
	
	if($CloudDevOpsMode -eq 1){
		# Write one + for each level of the pushd stack
		if ((get-location -stack).Count -gt 0) {
			# Write-Host " " -NoNewLine
			Write-Host (("+" * ((get-location -stack).Count))) -NoNewLine -ForegroundColor Cyan 
			Write-Host "$([char]27)[0m" -NoNewline
		}
		
		# Newline
		Write-Host "$([char]27)[0m :"
	}
	#$dateTimeSdate = get-date -Format "dd.MM.yyyy"
	#$dateTimeStime = get-date -Format "HH:mm:ss"
	$dateTimeSdate = get-date -Format "dd-MM-yy"
	$dateTimeStime = get-date -Format "HH:mm:ss"
	# Write-Host -back Red -fore Yellow "  $dateTimeSdate " -NoNewLine
	Write-Host -back Red "$([char]27)[38;5;5m  " -NoNewLine
	Write-Host -back Red -fore Yellow "  $dateTimeSdate " -NoNewLine
	Write-Host -back Green -fore Red "  " -NoNewLine
	# Write-Host -back Green -fore Yellow "  $dateTimeStime " -NoNewLine
	Write-Host -back Green -fore Yellow "  $dateTimeStime " -NoNewLine
	Write-Host -back Yellow -fore Green "  " -NoNewLine
	
	if ($null -ne (Get-Command "Get-GitDirectory" -ErrorAction Ignore)) {
		if (Get-GitDirectory -ne $null) { $DirectorySymbol="" } else { $DirectorySymbol="" }
		Write-Host -back Yellow -fore DarkBlue " $DirectorySymbol $(Split-Path -Path ($PWD) -Leaf) " -NoNewLine
		# Write-Host -back Yellow -fore DarkBlue " $DirectorySymbol $(Split-Path -Path ($PWD) -Leaf) " -NoNewLine
		$NextForegroundColor = "11"
	}
	
	if($DevMode -eq 1) {
		if ($null -ne (Get-Command "Get-GitDirectory" -ErrorAction Ignore)) {
			if (Get-GitDirectory -ne $null) {
				$GitPromptSettings.PathStatusSeparator = "$([char]27)[38;5;$($NextForegroundColor);48;5;25m  "
				$GitPromptSettings.AfterStatus.Text = " "
				$GitPromptSettings.BeforeStatus.Text = "  "
				$GitPromptSettings.BranchAheadStatusSymbol.Text = "^"
				$GitPromptSettings.BranchBehindStatusSymbol.Text = "<"
				$GitPromptSettings.BranchGoneStatusSymbol.Text = "X!"
				$GitPromptSettings.BranchBehindAndAheadStatusSymbol.Text = "<->"
				$GitPromptSettings.BranchIdenticalStatusSymbol.Text = ""
				$GitPromptSettings.BranchUntrackedText = "x"
				$GitPromptSettings.DelimStatus.Text = "||"
				$GitPromptSettings.LocalStagedStatusSymbol.Text = ""
				$GitPromptSettings.LocalWorkingStatusSymbol.Text = ""
				$GitPromptSettings.EnableStashStatus = $false
				$GitPromptSettings.ShowStatusWhenZero = $false
							
				Write-Host "$(Write-VcsStatus)" -NoNewLine
				$NextForegroundColor = "25"
			}
		}
	}
	
	if($CloudDevOpsMode -eq 0){
		# Write one + for each level of the pushd stack
		if ((get-location -stack).Count -gt 0) {
			# Write-Host " " -NoNewLine
			Write-Host (("+" * ((get-location -stack).Count))) -NoNewLine -ForegroundColor Cyan 
			Write-Host "$([char]27)[0m" -NoNewline
		}
	}
	Write-Host "$([char]27)[0m :"

    # Determine if the user is admin, so we color the prompt green or red
    $isAdmin = $false
    $isDesktop = ($PSVersionTable.PSEdition -eq "Desktop")

    if ($isDesktop -or $IsWindows) {
        $windowsIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent()
        $windowsPrincipal = new-object 'System.Security.Principal.WindowsPrincipal' $windowsIdentity
        $isAdmin = $windowsPrincipal.IsInRole("Administrators") -eq 1
    }
    else {
        $isAdmin = ((& id -u) -eq 0)
    }

    if ($isAdmin) { $color = "Red"; $promptText = "PSAD>" }
    else { $color = "Green"; $promptText = "PS>" }

    # Write PS> for desktop PowerShell, pwsh> for PowerShell Core
    if ($isDesktop) {
        Write-Host " $promptText" -NoNewLine -ForegroundColor $color
    }
    else {
        Write-Host " pwsh>" -NoNewLine -ForegroundColor $color
    }

    # Always have to return something or else we get the default prompt
    return " "
}
