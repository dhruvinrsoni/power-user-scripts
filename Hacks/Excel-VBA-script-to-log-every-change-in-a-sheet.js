Dim oldValue As Variant

Private Sub Workbook_SheetChange(ByVal Sh As Object, ByVal Target As Range)
    Dim wsLog As Worksheet
    Dim lRow As Long
    Dim logPassword As String

    logPassword = "LogPass" ' Password for the Change Log sheet

    ' Check if the Change Log sheet exists
    On Error Resume Next
    Set wsLog = ThisWorkbook.Sheets("Change Log")
    On Error GoTo 0

    ' If Change Log sheet does not exist, exit the sub
    If wsLog Is Nothing Then Exit Sub

    ' Only log changes on the "Use Cases" sheet
    If Sh.Name <> "Use Cases" Then Exit Sub

    ' Unprotect the Change Log sheet
    wsLog.Unprotect Password:=logPassword

    ' Find the next empty row in the Change Log sheet
    lRow = wsLog.Cells(wsLog.Rows.Count, 1).End(xlUp).Row + 1

    ' Log the change as Date	User	Sheet	Cell Changed	Old Value	New Value
    With wsLog
        .Cells(lRow, 1).Value = Now ' Log the current date and time
        .Cells(lRow, 2).Value = Application.UserName ' Log the username
        .Cells(lRow, 3).Value = Sh.Name ' Log the sheet name
        .Cells(lRow, 4).Value = Target.Address(False, False) ' Log the changed cell address in a readable format (e.g., E2)
        .Cells(lRow, 5).Value = oldValue ' Log the old value
        .Cells(lRow, 6).Value = Target.Value ' Log the new value
    End With

    ' Re-protect the Change Log sheet
    wsLog.Protect Password:=logPassword
End Sub

Private Sub Workbook_SheetSelectionChange(ByVal Sh As Object, ByVal Target As Range)
    ' Only track old values on the "Use Cases" sheet
    If Sh.Name <> "Use Cases" Then Exit Sub

    ' Store the old value in a variable
    oldValue = Target.Value
End Sub
