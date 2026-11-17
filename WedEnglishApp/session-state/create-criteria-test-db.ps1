$ErrorActionPreference='Stop'
$c=New-Object System.Data.SqlClient.SqlConnection('Server=(localdb)\mssqllocaldb;Database=master;Integrated Security=true;TrustServerCertificate=true');$c.Open()
try {
 $q=$c.CreateCommand();$q.CommandText="SELECT DB_ID(N'EnglishCenterCriteriaTest')";if($q.ExecuteScalar() -isnot [DBNull]){throw 'Test database already exists; refusing to replace.'}
 $q.CommandText="RESTORE FILELISTONLY FROM DISK=N'D:\LTUD\WedEnglishApp\session-state\db-backups\before-criteria-20261105.bak'";$r=$q.ExecuteReader();$files=@();while($r.Read()){$files+=@{Name=$r['LogicalName'];Type=$r['Type']}};$r.Close()
 $moves=($files | ForEach-Object {$ext=if($_.Type -eq 'L'){'ldf'}else{'mdf'};"MOVE N'$($_.Name.Replace("'","''"))' TO N'D:\LTUD\WedEnglishApp\session-state\db-backups\criteria-test.$ext'"}) -join ', '
 $q.CommandTimeout=180;$q.CommandText="RESTORE DATABASE [EnglishCenterCriteriaTest] FROM DISK=N'D:\LTUD\WedEnglishApp\session-state\db-backups\before-criteria-20261105.bak' WITH $moves";$null=$q.ExecuteNonQuery();Write-Output 'Created isolated test database.'
}finally{$c.Close()}
