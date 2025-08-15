# -*- coding: utf-8 -*-
import arcpy
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "PnP Global"
        self.alias = ""

        # List of tool classes associated with this toolbox
        self.tools = [CreateDomains,ArcDatabaseSettings]

class CreateDomains(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Domains"
        self.description = "Uses the lookup table to create domains"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
                                 displayName = "Lookup table",
                                 name = "lookupTable",
                                 datatype = "DETable",
                                 parameterType = "Required",
                                 direction = "Input")
        param1 = arcpy.Parameter(
                                 displayName = "Output workspace (where domains will be created)",
                                 name = "pnpWorkspace",
                                 datatype = "DEWorkspace",
                                 parameterType = "Required",
                                 direction = "Input")

        params = [param0, param1]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        sdeConnection = parameters[0].valueAsText #"Database Connections/pnpglobal_test1.sde"
        prefix = "PnPGlobal_test1.dbo"

        lookupTable = parameters[0].valueAsText #sdeConnection + "/" + prefix + ".lookups"

        inputWorkspace = os.path.dirname(lookupTable)

        outputWorkspace = parameters[1].valueAsText
        
        tableName = os.path.basename(lookupTable)

        prefix = tableName[:tableName.rfind(".")]

        domainnames = [row[0] for row in arcpy.da.SearchCursor(lookupTable, "domainname")]
        lookups = set(domainnames)
        messages.addMessage("lookups: " + str(lookups))

        for lookup in lookups:
            try:
                arcpy.CreateDatabaseView_management(inputWorkspace, lookup+"_VW","select * from domainlookups where domainname = '" + lookup + "'")
                messages.addMessage("Created view for "+lookup)
            except Exception as ex:
                #print "Warning:", sys.exc_info()[0]
                messages.addMessage("Warning creating view for " + lookup)
            try:
                viewName = prefix + "." + lookup + "_VW"
                arcpy.TableToDomain_management(os.path.join(inputWorkspace, viewName), "code", "value", outputWorkspace, lookup, lookup,"REPLACE")
                messages.addMessage("Created/updated domain for "+lookup)   
                arcpy.Delete_management(os.path.join(inputWorkspace, viewName),"Table")
            except Exception as ex:
                #print "Warning:", sys.exc_info()[0]
                messages.addErrorMessage("Error creating/updating domain for "+lookup)
                messages.addErrorMessage(sys.exc_info()[0])
                raise Exception()

        # Create range domains        
        messages.AddMessage("Creating range domains")
        try:
            arcpy.CreateDomain_management(outputWorkspace,"Percentage","Percentage","DOUBLE","RANGE","DEFAULT","DEFAULT")
            messages.AddMessage(arcpy.GetMessages())
            arcpy.SetValueForRangeDomain_management(outputWorkspace,"Percentage","0.0","1.0")
            arcpy.CreateDomain_management(outputWorkspace,"Latitude","Latitude","DOUBLE","RANGE","DEFAULT","DEFAULT")
            arcpy.SetValueForRangeDomain_management(outputWorkspace,"Latitude","-90.0","90.0")
            arcpy.CreateDomain_management(outputWorkspace,"Longitude","Longitude","DOUBLE","RANGE","DEFAULT","DEFAULT")
            arcpy.SetValueForRangeDomain_management(outputWorkspace,"Longitude","-180.0","180.0")
        except Exception as ex:
            messages.AddMessage("Range domains already exist and tied to feature classes")
        return

class ArcDatabaseSettings(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Create Defaults, Relationship Classes and Editor Tracking"
        self.description = "Creates default values, relationship classes and editor tracking for PnP Global geodatabase"
        self.canRunInBackground = True

    def getParameterInfo(self):
        """Define parameter definitions"""
        param0 = arcpy.Parameter(
                                 displayName = "PnP Workspace",
                                 name = "pnpWorkspace",
                                 datatype = "DEWorkspace",
                                 parameterType = "Required",
                                 direction = "Input")

        params = [param0]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        inputWorkspace = parameters[0].valueAsText

        arcpy.env.workspace = inputWorkspace

        messages.AddMessage("Assigning domains for LOCATION")
        arcpy.AssignDomainToField_management("LOCATION","versionTransactionType","TransactionType","#")
        arcpy.AssignDomainToField_management("LOCATION","proportionalFac","Percentage","#")
        arcpy.AssignDomainToField_management("LOCATION","rsaShareRetainedProdOp","Percentage","#")
        arcpy.AssignDomainToField_management("LOCATION","rsaShareCededSurplus","Percentage","#")
        arcpy.AssignDomainToField_management("LOCATION","rsaShareCededGroup","Percentage","#")
        arcpy.AssignDomainToField_management("LOCATION","currency","Currency","#")


        #arcpy.AssignDomainToField_management("CATASTROPHEZONE","code","CatastropheZone","#")

        messages.AddMessage("Assigning domains for CATASTROPHELIMIT")
        #arcpy.AssignDomainToField_management("CATASTROPHELIMIT","catastropheZone","CatastropheZone","#")
        arcpy.AssignDomainToField_management("CATASTROPHELIMIT","percentageDeductible","Percentage","#")
        arcpy.AssignDomainToField_management("CATASTROPHELIMIT","excluded","YesNo","#")
        arcpy.AssignDomainToField_management("CATASTROPHELIMIT","currency","Currency","#")

        messages.AddMessage("Assigning domains for ITEM")
        arcpy.AssignDomainToField_management("ITEM","item","Item","#")
        arcpy.AssignDomainToField_management("ITEM","inflationProvision","Percentage","#")
        arcpy.AssignDomainToField_management("ITEM","percentageDeductible","Percentage","#")
        arcpy.AssignDomainToField_management("ITEM","currency","Currency","#")

        messages.AddMessage("Assigning domains for LOCATIONNPFAC")
        arcpy.AssignDomainToField_management("LOCATIONNPFAC","peril","Peril","#")
        arcpy.AssignDomainToField_management("LOCATIONNPFAC","percentageCededFac","Percentage","#")
        arcpy.AssignDomainToField_management("LOCATIONNPFAC","currency","Currency","#")

        messages.AddMessage("Assigning domains for POLICYNPFAC")
        arcpy.AssignDomainToField_management("POLICYNPFAC","peril","Peril","#")
        arcpy.AssignDomainToField_management("POLICYNPFAC","percentageCededFac","Percentage","#")
        arcpy.AssignDomainToField_management("POLICYNPFAC","currency","Currency","#")

        messages.AddMessage("Assigning domains for LOCATIONPERIL")
        arcpy.AssignDomainToField_management("LOCATIONPERIL","peril","Peril","#")
        arcpy.AssignDomainToField_management("LOCATIONPERIL","excluded","YesNo","#")
        arcpy.AssignDomainToField_management("LOCATIONPERIL","percentageDeductible","Percentage","#")
        arcpy.AssignDomainToField_management("LOCATIONPERIL","currency","Currency","#")

        messages.AddMessage("Assigning domains for POLICY")
        arcpy.AssignDomainToField_management("POLICY","producingOperation","ProducingOperation","#")
        arcpy.AssignDomainToField_management("POLICY","lineOfBusiness","LineOfBusiness","#")
        arcpy.AssignDomainToField_management("POLICY","policySystem","PolicySystem","#")
        arcpy.AssignDomainToField_management("POLICY","leadFollow","LeadFollow","#")
        arcpy.AssignDomainToField_management("POLICY","xolLayered","YesNo","#")
        arcpy.AssignDomainToField_management("POLICY","currency","Currency","#")
        arcpy.AssignDomainToField_management("POLICY","grossNet","GrossNet","#")

        messages.AddMessage("Assigning domains for POLICYLAYER")
        arcpy.AssignDomainToField_management("POLICYLAYER","producingCountry","Country","#")
        arcpy.AssignDomainToField_management("POLICYLAYER","layerLimitApplies","YesNo","#")
        arcpy.AssignDomainToField_management("POLICYLAYER","rsaShare","Percentage","#")
        arcpy.AssignDomainToField_management("POLICYLAYER","proportionalFac","Percentage","#")
        arcpy.AssignDomainToField_management("POLICYLAYER","currency","Currency","#")

        messages.AddMessage("Assigning domains for POLICYPERIL")
        arcpy.AssignDomainToField_management("POLICYPERIL","peril","Peril","#")
        arcpy.AssignDomainToField_management("POLICYPERIL","excluded","YesNo","#")
        arcpy.AssignDomainToField_management("POLICYPERIL","percentageDeductible","Percentage","#")
        arcpy.AssignDomainToField_management("POLICYPERIL","currency","Currency","#")

        messages.AddMessage("Assigning domains for LOCATIONADDRESS")
        arcpy.AssignDomainToField_management("LOCATIONADDRESS","country","Country","#")
        arcpy.AssignDomainToField_management("LOCATIONADDRESS","latitude","Latitude","#")
        arcpy.AssignDomainToField_management("LOCATIONADDRESS","longitude","Longitude","#")
        arcpy.AssignDomainToField_management("LOCATIONADDRESS","geocodeAccuracy","GeocodeAccuracy","#")
        arcpy.AssignDomainToField_management("LOCATIONADDRESS","addressType","AddressType","#")
        arcpy.AssignDomainToField_management("LOCATIONADDRESS","geocodeSource","GeocodeSource","#")

        messages.AddMessage("Assigning domains for GEOCODERACCURACYMAPPING")
        arcpy.AssignDomainToField_management("GEOCODERACCURACYMAPPING","Geocoder","GeocodeSource","#")
        arcpy.AssignDomainToField_management("GEOCODERACCURACYMAPPING","GeocodeAccuracy","GeocodeAccuracy","#")

        messages.AddMessage("Assigning domains for COUNTRYCONFIG")
        arcpy.AssignDomainToField_management("COUNTRYCONFIG","ISO2","Country","#")
        arcpy.AssignDomainToField_management("COUNTRYCONFIG","Lat","Latitude","#")
        arcpy.AssignDomainToField_management("COUNTRYCONFIG","Lng","Longitude","#")
        arcpy.AssignDomainToField_management("COUNTRYCONFIG","CurrencyCode","Currency","#")
        arcpy.AssignDomainToField_management("COUNTRYCONFIG","MinAccuracy","GeocodeAccuracy","#")
        arcpy.AssignDomainToField_management("COUNTRYCONFIG","PrimaryGeocoder","GeocodeSource","#")
        arcpy.AssignDomainToField_management("COUNTRYCONFIG","SecondaryGeocoder","GeocodeSource","#")

        messages.AddMessage("Assigning domains for CURRENCYRATES")
        arcpy.AssignDomainToField_management("CURRENCYRATES","CurrFrom","Currency","#")
        arcpy.AssignDomainToField_management("CURRENCYRATES","CurrTo","Currency","#")

		# SN: removed as BATCHPROCESSJOB doesnt have an Action field or domain. No domain called Action.
        #messages.AddMessage("Assigning domains for BATCHPROCESSJOB")
        #arcpy.AssignDomainToField_management("BatchProcessJob","Action","Action","#")

        messages.AddMessage("Creating relationship classes")
        arcpy.CreateRelationshipClass_management("LOCATION","LOCATIONPERIL","REL_LOCATION_LOCATIONPERIL","COMPOSITE","LOCATIONPERIL","LOCATION","NONE","ONE_TO_MANY","NONE","ObjectID","FK_LOCATION_ObjectID","#","#")
        arcpy.CreateRelationshipClass_management("LOCATION","ITEM","REL_LOCATION_ITEM","COMPOSITE","ITEM","LOCATION","NONE","ONE_TO_MANY","NONE","ObjectID","FK_LOCATION_ObjectID","#","#")
        arcpy.CreateRelationshipClass_management("LOCATION","LocationNPFac","REL_LOCATION_LOCATIONNPFAC","COMPOSITE","LOCATIONNPFAC","LOCATION","NONE","ONE_TO_MANY","NONE","ObjectID","FK_LOCATION_ObjectID","#","#")
        arcpy.CreateRelationshipClass_management("POLICY","Location","REL_POLICY_LOCATION","COMPOSITE","LOCATION","POLICY","NONE","ONE_TO_MANY","NONE","ObjectID","FK_POLICY_ObjectID","#","#")
        arcpy.CreateRelationshipClass_management("POLICY","PolicyLayer","REL_POLICY_POLICYLAYER","COMPOSITE","POLICYLAYER","POLICY","NONE","ONE_TO_MANY","NONE","ObjectID","FK_POLICY_ObjectID","#","#")
        arcpy.CreateRelationshipClass_management("POLICYLAYER","PolicyNPFac","REL_POLICYLAYER_POLICYNPFAC","COMPOSITE","POLICYNPFAC","POLICYLAYER","NONE","ONE_TO_MANY","NONE","ObjectID","FK_POLICYLAYER_ObjectID","#","#")
        arcpy.CreateRelationshipClass_management("POLICY","PolicyPeril","REL_POLICY_POLICYPERIL","COMPOSITE","POLICYPERIL","POLICY","NONE","ONE_TO_MANY","NONE","ObjectID","FK_POLICY_ObjectID","#","#")
        arcpy.CreateRelationshipClass_management("POLICYPERIL","CATASTROPHELIMIT","REL_POLICYPERIL_CATLIMIT","COMPOSITE","CATASTROPHELIMIT","POLICYPERIL","NONE","ONE_TO_MANY","NONE","ObjectID","FK_POLICYPERIL_ObjectID","#","#")
        arcpy.CreateRelationshipClass_management("Location","LocationAddress","REL_LOCATION_LOCATIONADDRESS","COMPOSITE","LOCATIONADDRESS","LOCATION","NONE","ONE_TO_MANY","NONE","ObjectID","FK_LOCATION_ObjectID","#","#")
        arcpy.CreateRelationshipClass_management("CATASTROPHEZONE","CATASTROPHELIMIT","REL_CATASTROPHEZONE_CATASTROPHELIMIT","SIMPLE","CATASTROPHELIMIT","CATASTROPHEZONE","NONE","ONE_TO_MANY","NONE","code","catastropheZone","#","#")
        

        messages.AddMessage("Assigning default values to POLICY")
        # Execute AssignDefaultToField
        arcpy.AssignDefaultToField_management("POLICY", "expiryExtension",0)
        arcpy.AssignDefaultToField_management("POLICY", "xolLayered","N")
        arcpy.AssignDefaultToField_management("POLICY", "lossLimit",0)
        arcpy.AssignDefaultToField_management("POLICY", "materialDamageLimit",0)
        arcpy.AssignDefaultToField_management("POLICY", "businessInterruptionLimit",0)
        arcpy.AssignDefaultToField_management("POLICY", "versionNumber",0)
        arcpy.AssignDefaultToField_management("POLICY", "grossNet","GRO")

        messages.AddMessage("Assigning default values to POLICYLAYER")
        arcpy.AssignDefaultToField_management("POLICYLAYER", "layerIdentifier","PRIMARY")
        arcpy.AssignDefaultToField_management("POLICYLAYER", "attachmentPoint",0)
        arcpy.AssignDefaultToField_management("POLICYLAYER", "layerLimitApplies","N")
        arcpy.AssignDefaultToField_management("POLICYLAYER", "rsaShare",1)

        messages.AddMessage("Assigning default values to POLICYNPFAC")
        arcpy.AssignDefaultToField_management("POLICYNPFAC", "attachmentPoint",0)
        arcpy.AssignDefaultToField_management("POLICYNPFAC", "facAmount",0)

        messages.AddMessage("Assigning default values to POLICYPERIL")
        arcpy.AssignDefaultToField_management("POLICYPERIL", "excluded","N")
        arcpy.AssignDefaultToField_management("POLICYPERIL", "materialDamageDeductible",0)
        arcpy.AssignDefaultToField_management("POLICYPERIL", "businessInterruptionDeductible",0)

        messages.AddMessage("Assigning default values to CATASTROPHELIMIT")
        arcpy.AssignDefaultToField_management("CATASTROPHELIMIT", "lossLimit",0)
        arcpy.AssignDefaultToField_management("CATASTROPHELIMIT", "percentageDeductible", 0)
        arcpy.AssignDefaultToField_management("CATASTROPHELIMIT", "materialDamageDeductible",0)
        arcpy.AssignDefaultToField_management("CATASTROPHELIMIT", "businessInterruptionDeductible",0)
        arcpy.AssignDefaultToField_management("CATASTROPHELIMIT", "excluded","N")

        messages.AddMessage("Assigning default values to LOCATION")
        arcpy.AssignDefaultToField_management("LOCATION", "versionNumber",0)
        arcpy.AssignDefaultToField_management("LOCATION", "grossTotalSumInsured",0)
        arcpy.AssignDefaultToField_management("LOCATION", "grossTotalInsuredValue",0)
        arcpy.AssignDefaultToField_management("LOCATION", "grossEstimatedMaximumLoss",0)
        arcpy.AssignDefaultToField_management("LOCATION", "grossProbableMaximumLoss",0)
        arcpy.AssignDefaultToField_management("LOCATION", "grossNormalLossExpectancy",0)
        arcpy.AssignDefaultToField_management("LOCATION", "netTotalSumInsured",0)
        arcpy.AssignDefaultToField_management("LOCATION", "netTotalInsuredValue",0)
        arcpy.AssignDefaultToField_management("LOCATION", "netEstimatedMaximumLoss",0)
        arcpy.AssignDefaultToField_management("LOCATION", "netProbableMaximumLoss",0)
        arcpy.AssignDefaultToField_management("LOCATION", "netNormalLossExpectancy",0)
        arcpy.AssignDefaultToField_management("LOCATION", "lossLimit",0)
        arcpy.AssignDefaultToField_management("LOCATION", "materialDamageLimit",0)
        arcpy.AssignDefaultToField_management("LOCATION", "businessInterruptionLimit",0)

        messages.AddMessage("Assigning default values to ITEM")
        arcpy.AssignDefaultToField_management("ITEM", "grossSumInsured",0)
        arcpy.AssignDefaultToField_management("ITEM", "netSumInsured",0)
        arcpy.AssignDefaultToField_management("ITEM", "inflationProvision",0)
        arcpy.AssignDefaultToField_management("ITEM", "percentageDeductible",0)

        messages.AddMessage("Assigning default values to LOCATIONPERIL")
        arcpy.AssignDefaultToField_management("LOCATIONPERIL", "excluded","N")
        arcpy.AssignDefaultToField_management("LOCATIONNPFAC", "attachmentPoint",0)
        arcpy.AssignDefaultToField_management("LOCATIONNPFAC", "facAmount",0)

        messages.AddMessage("Assigning default values to CATASTROPHEZONE")
        arcpy.AssignDefaultToField_management("CATASTROPHEZONE", "code", "XXX")

        # Execute enable editor tracking
        messages.AddMessage("Enabling editor tracking")
        arcpy.EnableEditorTracking_management("CATASTROPHEZONE","createdBy","dateCreated","modifiedBy","dateModified")
        arcpy.EnableEditorTracking_management("LOCATION","createdBy","dateCreated","modifiedBy","dateModified")
        arcpy.EnableEditorTracking_management("POLICY","createdBy","dateCreated","modifiedBy","dateModified")
        arcpy.EnableEditorTracking_management("COUNTRYCONFIG","CreatedBy","DateCreated","LastUpdatedBy","DateLastUpdated")
        arcpy.EnableEditorTracking_management("CURRENCYRATES","CreatedBy","DateCreated","LastUpdatedBy","DateLastUpdated")
        arcpy.EnableEditorTracking_management("DOMAINLOOKUPS","CreatedBy","DateCreated","LastUpdatedBy","DateLastUpdated")
        arcpy.EnableEditorTracking_management("GEOCODERACCURACYMAPPING","CreatedBy","DateCreated","LastUpdatedBy","DateLastUpdated")

        return
