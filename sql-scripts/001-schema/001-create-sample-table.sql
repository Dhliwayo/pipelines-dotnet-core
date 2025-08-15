-- Sample table creation script
-- This script demonstrates the deployment pipeline functionality

-- Check if table already exists to make script idempotent
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'SampleTable')
BEGIN
    CREATE TABLE SampleTable (
        Id INT IDENTITY(1,1) PRIMARY KEY,
        Name NVARCHAR(100) NOT NULL,
        Description NVARCHAR(500) NULL,
        CreatedDate DATETIME2 DEFAULT GETDATE(),
        ModifiedDate DATETIME2 DEFAULT GETDATE()
    )
    
    PRINT 'SampleTable created successfully'
END
ELSE
BEGIN
    PRINT 'SampleTable already exists - skipping creation'
END

-- Add a comment to the table for documentation
EXEC sp_addextendedproperty 
    @name = N'MS_Description', 
    @value = N'Sample table created by deployment pipeline', 
    @level0type = N'SCHEMA', 
    @level0name = N'dbo', 
    @level1type = N'TABLE', 
    @level1name = N'SampleTable'
