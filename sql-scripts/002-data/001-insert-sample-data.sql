-- Sample data insertion script
-- This script demonstrates inserting sample data into the SampleTable

-- Check if data already exists to make script idempotent
IF NOT EXISTS (SELECT * FROM SampleTable WHERE Name = 'Sample Record 1')
BEGIN
    INSERT INTO SampleTable (Name, Description)
    VALUES 
        ('Sample Record 1', 'This is the first sample record created by the deployment pipeline'),
        ('Sample Record 2', 'This is the second sample record created by the deployment pipeline'),
        ('Sample Record 3', 'This is the third sample record created by the deployment pipeline')
    
    PRINT 'Sample data inserted successfully'
END
ELSE
BEGIN
    PRINT 'Sample data already exists - skipping insertion'
END

-- Display the current data
SELECT 
    Id,
    Name,
    Description,
    CreatedDate,
    ModifiedDate
FROM SampleTable
ORDER BY Id
