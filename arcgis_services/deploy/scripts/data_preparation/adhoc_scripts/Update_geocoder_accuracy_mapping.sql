INSERT INTO [dbo].[GEOCODERACCURACYMAPPING]
           ([Geocoder]
           ,[EntityType]
           ,[GeocodeAccuracy],
		    [ObjectID]
		   )
     VALUES
           (
		   'EAC'
           ,'building_group'
           ,'STC'
		   ,(SELECT MAX(ObjectID)+1 FROM [GLOBAL_EXPOSURE].[dbo].[GEOCODERACCURACYMAPPING])
		   )

	USE [GLOBAL_EXPOSURE]
GO;