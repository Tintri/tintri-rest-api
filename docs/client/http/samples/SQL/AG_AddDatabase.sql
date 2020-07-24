--- YOU MUST EXECUTE THE FOLLOWING SCRIPT IN SQLCMD MODE.
--Assumes only 1 data and 1 log file and the databasename is the same as the logical filename
--Works with only 2 nodes, if you have multiple nodes need to run again or modify script
:setvar AGGroup TSIS-AG1
:setvar AGPrimary TSIS-AG-NODE2
:setvar AGSecondary TSIS-AG-NODE1
:setvar Database AdventureWorks2017
:setvar BackupPath \\Win16-SMBhost.ttucs.tm.tintri.com\SQLBackup\AG
:setvar DestinationPath \\hqtm-t5040-data.ttucs.tm.tintri.com\db\TSIS-AG-NODE1\Data

:Connect $(AGPrimary)

--RESTORE FILELISTONLY FROM DISK = N'\\Win16-SMBhost.ttucs.tm.tintri.com\SQLBackup\AG\AdventureWorks2017.bak'

USE [master]
GO
ALTER AVAILABILITY GROUP [$(AGGroup)]
MODIFY REPLICA ON N'$(AGPrimary)' WITH (SEEDING_MODE = MANUAL)
GO

USE [master]
GO
ALTER AVAILABILITY GROUP [$(AGGroup)]
ADD DATABASE [$(Database)];
GO

:Connect $(AGPrimary)

BACKUP DATABASE [$(Database)] TO  DISK = N'$(BackupPath)\$(Database).bak' WITH COPY_ONLY, FORMAT, INIT, SKIP, REWIND, NOUNLOAD, COMPRESSION,  STATS = 5
GO


:Connect $(AGSecondary)

RESTORE DATABASE [$(Database)] FROM  DISK = N'$(BackupPath)\$(Database).bak' 
WITH  FILE = 1,  MOVE N'$(Database)' TO N'$(DestinationPath)\$(Database).mdf',  
MOVE N'$(Database)_log' TO N'$(DestinationPath)\$(Database).ldf', 
NORECOVERY,  NOUNLOAD,  STATS = 5
GO

:Connect $(AGPrimary)

BACKUP LOG [$(Database)] TO  DISK = N'$(BackupPath)\$(Database).trn' WITH NOFORMAT, INIT, NOSKIP, REWIND, NOUNLOAD, COMPRESSION,  STATS = 5
GO

:Connect $(AGSecondary)

RESTORE LOG [$(Database)] FROM  DISK = N'$(BackupPath)\$(Database).trn' WITH  NORECOVERY,  NOUNLOAD,  STATS = 5
GO



:Connect $(AGSecondary)

-- Wait for the replica to start communicating
begin try
declare @conn bit
declare @count int
declare @replica_id uniqueidentifier 
declare @group_id uniqueidentifier
set @conn = 0
set @count = 30 -- wait for 5 minutes 

if (serverproperty('IsHadrEnabled') = 1)
	and (isnull((select member_state from master.sys.dm_hadr_cluster_members where upper(member_name COLLATE Latin1_General_CI_AS) = upper(cast(serverproperty('ComputerNamePhysicalNetBIOS') as nvarchar(256)) COLLATE Latin1_General_CI_AS)), 0) <> 0)
	and (isnull((select state from master.sys.database_mirroring_endpoints), 1) = 0)
begin
    select @group_id = ags.group_id from master.sys.availability_groups as ags where name = N'$(AGGroup)'
	select @replica_id = replicas.replica_id from master.sys.availability_replicas as replicas where upper(replicas.replica_server_name COLLATE Latin1_General_CI_AS) = upper(@@SERVERNAME COLLATE Latin1_General_CI_AS) and group_id = @group_id
	while @conn <> 1 and @count > 0
	begin
		set @conn = isnull((select connected_state from master.sys.dm_hadr_availability_replica_states as states where states.replica_id = @replica_id), 1)
		if @conn = 1
		begin
			-- exit loop when the replica is connected, or if the query cannot find the replica status
			break
		end
		waitfor delay '00:00:10'
		set @count = @count - 1
	end
end
end try
begin catch
	-- If the wait loop fails, do not stop execution of the alter database statement
end catch
ALTER DATABASE [$(Database)] SET HADR AVAILABILITY GROUP = [$(AGGroup)];

GO


