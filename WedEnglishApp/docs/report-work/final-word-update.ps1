param([string]$DocumentPath,[string]$OutputPath,[string]$PdfPath)
$ErrorActionPreference='Stop'
$w=$null;$doc=$null
try {
 $w=New-Object -ComObject Word.Application;$w.Visible=$false;$w.DisplayAlerts=0
 $doc=$w.Documents.Open($DocumentPath,$false,$false)
 foreach($name in @('TOC 1','TOC 2','TOC 3')) {
  $s=$doc.Styles.Item($name);$s.Font.Name='Times New Roman';$s.Font.Size=12;$s.Font.Color=0;$s.Font.Bold=0
  $s.ParagraphFormat.SpaceAfter=3;$s.ParagraphFormat.SpaceBefore=0;$s.ParagraphFormat.LineSpacingRule=0;$s.ParagraphFormat.KeepWithNext=0
  $s.ParagraphFormat.TabStops.ClearAll();$null=$s.ParagraphFormat.TabStops.Add(453.5,2,1)
 }
 for($pass=0;$pass -lt 3;$pass++) {
  $null=$doc.Fields.Update()
  foreach($toc in $doc.TablesOfContents){$toc.Update();$toc.Range.Font.Name='Times New Roman';$toc.Range.Font.Size=12;$toc.Range.Font.Color=0;$toc.Range.ParagraphFormat.KeepWithNext=0}
  $doc.Repaginate()
 }
 $doc.SaveAs2($OutputPath,16);$doc.ExportAsFixedFormat($PdfPath,17)
 Write-Output ('Pages '+$doc.ComputeStatistics(2)+'; automatic lists '+$doc.TablesOfContents.Count)
} finally {if($doc){$doc.Close(0);[void][Runtime.InteropServices.Marshal]::ReleaseComObject($doc)};if($w){$w.Quit();[void][Runtime.InteropServices.Marshal]::ReleaseComObject($w)}}
