$ErrorActionPreference='Stop'
$src='D:/LTUD/7_NguyenKhanhHuy/16_NguyenKhanhHuy_baocaoLLUD.docx'
$out='D:/LTUD/7_NguyenKhanhHuy/16_NguyenKhanhHuy_baocaoLLUD_Muc_luc_tu_dong.docx'
$pdf='D:/LTUD/WedEnglishApp/docs/report-work/qa/user-toc.pdf'
$w=$null;$d=$null
try {
 $w=New-Object -ComObject Word.Application;$w.Visible=$false;$w.DisplayAlerts=0
 $d=$w.Documents.Open($src,$false,$true)
 $d.SaveAs2($out,16)
 if($d.TablesOfContents.Count -ne 3){throw 'Expected main contents plus table and figure lists.'}
 for($i=1;$i -le 3;$i++) {
  $toc=$d.TablesOfContents.Item($i)
  if($i -eq 1){$toc.UpperHeadingLevel=1;$toc.LowerHeadingLevel=3;$code=' TOC \o "1-3" \t "FrontMatterHeading,1" \h \z '}
  elseif($i -eq 2){$code=' TOC \h \z \t "NHKTableCaption,1" '}
  else{$code=' TOC \h \z \t "NHKFigureCaption,1,NHKSubFigureCaption,1" '}
  $toc.Range.Fields.Item(1).Code.Text=$code
  $toc.UseHyperlinks=$true;$toc.IncludePageNumbers=$true;$toc.RightAlignPageNumbers=$true;$toc.TabLeader=1
 }
 $width=$d.Sections.Item(2).PageSetup.PageWidth-$d.Sections.Item(2).PageSetup.LeftMargin-$d.Sections.Item(2).PageSetup.RightMargin
 for($level=1;$level -le 3;$level++) {
  $s=$d.Styles.Item('TOC '+$level);$s.Font.Name='Times New Roman';$s.Font.Size=12;$s.Font.Color=0;$s.Font.Bold=0
  $s.ParagraphFormat.SpaceBefore=0;$s.ParagraphFormat.SpaceAfter=3;$s.ParagraphFormat.LineSpacingRule=0
  $s.ParagraphFormat.LeftIndent=($level-1)*12;$s.ParagraphFormat.RightIndent=0;$s.ParagraphFormat.FirstLineIndent=0
  $s.ParagraphFormat.KeepWithNext=0;$s.ParagraphFormat.KeepTogether=-1
  $s.ParagraphFormat.TabStops.ClearAll();$null=$s.ParagraphFormat.TabStops.Add($width,2,1)
 }
 for($pass=0;$pass -lt 3;$pass++) {
  foreach($toc in $d.TablesOfContents){$toc.Update();$toc.Range.Font.Name='Times New Roman';$toc.Range.Font.Size=12;$toc.Range.Font.Color=0}
  $d.Repaginate()
 }
 $d.Save();$d.ExportAsFixedFormat($pdf,17)
 Write-Output ('Pages '+$d.ComputeStatistics(2)+'; automatic lists '+$d.TablesOfContents.Count)
 Write-Output $out
} finally {
 if($d){$d.Close(0);[void][Runtime.InteropServices.Marshal]::ReleaseComObject($d)}
 if($w){$w.Quit();[void][Runtime.InteropServices.Marshal]::ReleaseComObject($w)}
}
