$ErrorActionPreference='Stop'
$c=New-Object System.Data.SqlClient.SqlConnection('Server=(localdb)\mssqllocaldb;Database=master;Integrated Security=true;TrustServerCertificate=true');$c.Open()
try {$q=$c.CreateCommand();$q.CommandTimeout=180;$q.CommandText="BACKUP DATABASE [EnglishCenterDb] TO DISK=N'D:\LTUD\WedEnglishApp\session-state\db-backups\before-criteria-20261105.bak' WITH COPY_ONLY, INIT";$null=$q.ExecuteNonQuery();Write-Output 'Created COPY_ONLY database backup.'}finally{$c.Close()}
