param(
 [string]$DocumentPath='D:\LTUD\WedEnglishApp\docs\report-work\report-draft.docx',
 [string]$OutputPath='D:\LTUD\WedEnglishApp\Bao_cao_do_an_HITC_English_Nguyen_Khanh_Huy.docx',
 [string]$PdfPath='D:\LTUD\WedEnglishApp\docs\report-work\qa\report.pdf'
)
$ErrorActionPreference='Stop'
$wordReport=$null
$reportDoc=$null
try {
 $wordReport=New-Object -ComObject Word.Application
 $wordReport.Visible=$false
 $wordReport.DisplayAlerts=0
 $reportDoc=$wordReport.Documents.Open($DocumentPath,$false,$false)
 $null=$reportDoc.Fields.Update()
 foreach($tocItem in $reportDoc.TablesOfContents){$tocItem.Update()}
 foreach($figureList in $reportDoc.TablesOfFigures){$figureList.Update()}
 foreach($figureList in $reportDoc.TablesOfFigures){
  $figureList.Range.Font.Name='Times New Roman'
  $figureList.Range.Font.Size=11
  $figureList.Range.ParagraphFormat.SpaceAfter=0
  $figureList.Range.ParagraphFormat.SpaceBefore=0
  $figureList.Range.ParagraphFormat.LineSpacingRule=4
  $figureList.Range.ParagraphFormat.LineSpacing=13.5
 }
 $reportDoc.Repaginate()
 foreach($tocItem in $reportDoc.TablesOfContents){$tocItem.Update()}
 foreach($figureList in $reportDoc.TablesOfFigures){$figureList.Update()}
 foreach($figureList in $reportDoc.TablesOfFigures){
  $figureList.Range.Font.Size=11
  $figureList.Range.ParagraphFormat.SpaceAfter=0
  $figureList.Range.ParagraphFormat.SpaceBefore=0
  $figureList.Range.ParagraphFormat.LineSpacingRule=4
  $figureList.Range.ParagraphFormat.LineSpacing=13.5
 }
 $reportDoc.Repaginate()
 $reportDoc.SaveAs2($OutputPath,16)
 $reportDoc.ExportAsFixedFormat($PdfPath,17)
 Write-Output ('Pages: '+$reportDoc.ComputeStatistics(2))
 Write-Output ('TOC: '+$reportDoc.TablesOfContents.Count+' Figure lists: '+$reportDoc.TablesOfFigures.Count)
 Write-Output ('Saved '+$OutputPath)
} finally {
 if($null -ne $reportDoc){$reportDoc.Close(0);[void][Runtime.InteropServices.Marshal]::ReleaseComObject($reportDoc)}
 if($null -ne $wordReport){$wordReport.Quit();[void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordReport)}
}
