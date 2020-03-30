import os, sys, arcpy, datetime, traceback
from arcpy import env

if len(sys.argv) < 2: 
    Version = ""
    Vnum = ""
    LDMversion = ""
    PDMname = ""
    pFolder = ""
else:
    Version = str(sys.argv[1])
    Vnum = str(sys.argv[2])
    LDMversion = str(sys.argv[3])
    PDMname = str(sys.argv[4])
    pFolder = str(sys.argv[5])

    LDMtoPDM = str(sys.argv[6])

    runSourceSchema = str(sys.argv[7])
    runDomains = str(sys.argv[8])
    runSubtypes_All = str(sys.argv[9])
    runRelationships = str(sys.argv[10])
    runRelationshipsAtt = str(sys.argv[11])
    runGeometricNetwork = str(sys.argv[12])
    runMetadataExporter = str(sys.argv[13])
        
LDMtoPDM = "No"

##Version = "20161012_085332"
##Vnum = "RunTest"
##PDMname = "Draft_PDM4_0BuildY"
##pFolder = "C:\Workspace\Projects\LDMtoPDM_BuildY\TestingPGDBtoFGDB"

try:
    inGDB = pFolder + "\\" + Vnum + "\\" + "Step02_PDM\PDM" + "\\" + PDMname + "_" + Version + ".mdb"
    inFolder = pFolder + "\\" + Vnum + "\\" + "Step03_GDBInfo"

    # LDM to PDM
    if LDMtoPDM == "Yes":
        NoGeomNet = inGDB[:-4] + "_v7metaNoGeomNet.gdb"
        GeomNet = inGDB[:-4] + "_v8GeomNet.gdb"
    else:
        NoGeomNet = r"M:\Projects\SchemaInfo\Navy_4_1_Utilities\Navy_4_1_Utilities02.gdb"
        GeomNet = r"M:\Projects\SchemaInfo\Navy_4_1_Utilities\Navy_4_1_Utilities02.gdb"
    
    dFolderDate = os.path.basename(inGDB[:-4])[-15:]

##    Which to process
##    runSourceSchema = "Yes"
##    runDomains = "Yes"
##    runSubtypes_All = "Yes"
##    runRelationships = "Yes"
##    runRelationshipsAtt = "Yes"
##    runGeometricNetwork = "Yes"
##    runMetadataExporter = "Yes"
    
    workingDIR = inFolder + "\\" + "GDBInfo"
    if not os.path.exists(workingDIR): os.makedirs(workingDIR)

    def DetermineGeodatabaseType(inGeodatabase):
        try:
            length = len(inGeodatabase)
            starting_pos = length - 4
            geodatabaseType = inGeodatabase[starting_pos:length]
            if geodatabaseType == ".sde":
                outGeodatabaseType = "SDE"
            if geodatabaseType == ".mdb":
                outGeodatabaseType = "PersonalGDB"
            if geodatabaseType == ".gdb":
                outGeodatabaseType = "FileGDB"
            if geodatabaseType == ".shp":
                outGeodatabaseType = "Shapefile"
            return outGeodatabaseType
        except:
            ErrDesc = "Error: Failed in parsing the inputs."
            raise StandardError, ErrDesc

    # def to find unique values for a field
    def unique_values(table, field):
        with arcpy.da.SearchCursor(table, [field]) as cursor:
            return sorted({row[0] for row in cursor if row[0]}) # to remove nulls and blanks
    def remove_values_from_list(the_list, val):
        return [value for value in the_list if value != val]

    workspace_type = DetermineGeodatabaseType(NoGeomNet)

    # Will overwrite table views for example.
    arcpy.env.overwriteOutput = True

    totalStartTime = datetime.datetime.now()
    startTime = datetime.datetime.now()

##    # Logging
##    if not arcpy.Exists(workingDIR + "\\logFiles"):
##        arcpy.CreateFolder_management(workingDIR, "logFiles")
##    outLogFileFolder = workingDIR + "\\logFiles"
##
##    logging = os.sep.join([outLogFileFolder, "SourceInfoLog_" + dFolderDate + ".txt".format()])
##    loggingOpen = open(logging,"w")
##
##    print "inGDB: " + inGDB + "\n" + "Output Results Folder: " + workingDIR + "\n" + str(startTime)
##    loggingOpen.write('{0}\n'.format("inGDB: " + inGDB + "\n" + "Output Results Folder: " + workingDIR + "\n" + str(startTime)))

    # Logging
    outLogFileFolder = pFolder + "\\" + Vnum + "\\logFiles"
    if not os.path.exists(outLogFileFolder): os.makedirs(outLogFileFolder)

    if os.path.exists(outLogFileFolder + "\\" + "SchemaLog_" + dFolderDate + ".txt"):
        arcpy.Delete_management(outLogFileFolder + "\\" + "SchemaLog_" + dFolderDate + ".txt")
        
    logging = os.sep.join([outLogFileFolder, "SchemaLog_" + dFolderDate + ".txt".format()])

    def addLog(log):
        print log
        loggingOpen = open(logging,"a")
        loggingOpen.write('{0}\n'.format(log))
        loggingOpen.close()

    ####################
    ##  SourceSchema  ##
    ####################

    if runSourceSchema == "Yes":
        
        # Output database and tables
        infoGDBname = "schemaInfo_PDM_" + dFolderDate
        if not arcpy.Exists(workingDIR + "\\" + infoGDBname + ".mdb"):
            arcpy.CreatePersonalGDB_management(workingDIR, infoGDBname, "CURRENT")
        infoGDB = workingDIR + "\\" + infoGDBname + ".mdb"

        sourceSchemaName = "SourceSchema"
        if arcpy.Exists(infoGDB + "\\" + sourceSchemaName):
            arcpy.Delete_management(infoGDB + "\\" + sourceSchemaName)
            arcpy.CreateTable_management(infoGDB, sourceSchemaName, "", "")
        else:
            arcpy.CreateTable_management(infoGDB, sourceSchemaName, "", "")
        sourceSchemaTable = infoGDB + "\\" + sourceSchemaName

        sourceSchemaTableView = "sourceSchemaTableView"
        arcpy.MakeTableView_management(sourceSchemaTable, sourceSchemaTableView)

        addLog("Creating " + sourceSchemaName + " Table")

        arcpy.AddField_management(sourceSchemaTableView, "FDS_or_Root", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "SourceName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "SourceAlias", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "SourceType", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "FieldName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "FieldAlias", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "FieldType", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "FieldLength", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "FieldEditable", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "FieldIsNullable", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "FieldPrecision", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "FieldRequired", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "FieldScale", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "FieldDefaultValue", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceSchemaTableView, "DomainName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")

        # Setting up InsertCursor 
        cursorSchemaTable = arcpy.da.InsertCursor(sourceSchemaTableView,("FDS_or_Root","SourceName","SourceAlias","SourceType","FieldName","FieldAlias","FieldType","FieldLength","FieldEditable","FieldIsNullable","FieldPrecision","FieldRequired","FieldScale","FieldDefaultValue","DomainName"))

        arcpy.env.workspace = NoGeomNet

        for fds in arcpy.ListDatasets('','Feature') + ['']:
            if len(str(fds)) == 0:
                tableList = arcpy.ListTables()
                
                ##  Tables on Root of GDB
                for table in tableList:

                    tblView = "tblView"
                    arcpy.MakeTableView_management(table, tblView)

                    if workspace_type == "SDE":
                        tableSplit = (table.split("."))[2]
                    else:
                        tableSplit = table

                    addLog("\tTable on Root | " + tableSplit)

                    fieldList = arcpy.ListFields(tblView)
                    desc = arcpy.Describe(table)

                    for field in fieldList:

                        if field.name.upper() == 'OBJECTID':continue
                        if field.name.upper().startswith("SHAPE"): continue
                        
                        cursorSchemaTable.insertRow(("Root", tableSplit, desc.aliasName, "Table",
                                                     field.name, field.aliasName, field.type, str(field.length),
                                                     field.editable, field.isNullable, field.precision, field.required,
                                                     field.scale, field.defaultValue, field.domain))
                    arcpy.Delete_management(tblView)
                    
                ## Feature Classes on Root of GDB
                for fc in arcpy.ListFeatureClasses('',''):

                    rootfcLyr = "rootfcLyr"
                    arcpy.MakeFeatureLayer_management(fc, rootfcLyr)

                    desc = arcpy.Describe(fc)

                    ## Do not process Anno
                    if desc.featureType == "Simple": 

                        if workspace_type == "SDE":
                            fcSplit = (fc.split("."))[2]
                        else:
                            fcSplit = fc

                        addLog("\tFC on Root | " + fcSplit)
                        
                        fieldList = arcpy.ListFields(rootfcLyr)

                        for field in fieldList:

                            if field.name.upper() == 'OBJECTID':continue
                            if field.name.upper().startswith("SHAPE"): continue

                            cursorSchemaTable.insertRow(("Root", fc, desc.aliasName, desc.shapeType,
                                                         field.name, field.aliasName, field.type, str(field.length),
                                                         field.editable, field.isNullable, field.precision, field.required,
                                                         field.scale, field.defaultValue, field.domain))
                    arcpy.Delete_management(rootfcLyr)
            else:
                ## Feature Classes inside Feature Datasets
                for fc in arcpy.ListFeatureClasses('','',fds):

                    fcLyr = "fcLyr"
                    arcpy.MakeFeatureLayer_management(fc, fcLyr)

                    desc = arcpy.Describe(fc)

                    ## Do not process Anno
                    if desc.featureType == "Simple":

                        if workspace_type == "SDE":
                            fdsSplit = (fds.split("."))[2]
                            fcSplit = (fc.split("."))[2]
                        else:
                            fdsSplit = fds
                            fcSplit = fc

                        addLog("\tFC in FDS | " + fdsSplit + " | " + fcSplit)

                        fieldList = arcpy.ListFields(fcLyr)
                        desc = arcpy.Describe(fc)

                        ##  A check to make sure FDS is not the same name as the FC
                        if desc.dataType == "FeatureClass":
                            
                            for field in fieldList:

                                if field.name.upper() == 'OBJECTID':continue
                                if field.name.upper().startswith("SHAPE"): continue
                                cursorSchemaTable.insertRow((fds, fc, desc.aliasName, desc.shapeType, field.name, field.aliasName,
                                                             field.type, str(field.length),
                                                             field.editable, field.isNullable, field.precision, field.required,
                                                             field.scale, field.defaultValue, field.domain))
                    arcpy.Delete_management(fcLyr)
                
        addLog("Schema Processing Time: " + str((datetime.datetime.now()-startTime)))

        del cursorSchemaTable
        arcpy.Delete_management(sourceSchemaTableView)
    
    ###############
    ##  Domains  ##
    ###############

    if runDomains == "Yes":

        # Output database and tables
        infoGDBname = "schemaInfo_PDM_" + dFolderDate
        if not arcpy.Exists(workingDIR + "\\" + infoGDBname + ".mdb"):
            arcpy.CreatePersonalGDB_management(workingDIR, infoGDBname, "CURRENT")
        infoGDB = workingDIR + "\\" + infoGDBname + ".mdb"

        domainTime = datetime.datetime.now()

        sourceNameTable = infoGDB + "\\" + "Domains"
        if arcpy.Exists(sourceNameTable):
            arcpy.Delete_management(sourceNameTable)
            arcpy.CreateTable_management(infoGDB, "Domains", "", "")
        else:
            arcpy.CreateTable_management(infoGDB, "Domains", "", "")

        domainTableView = "domainTableView"
        arcpy.MakeTableView_management(infoGDB + "\\Domains", domainTableView)

        addLog("\nCreating " + "Domains Table")

        arcpy.AddField_management(domainTableView, "DomainName", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(domainTableView, "DomainType", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(domainTableView, "DomainRange", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(domainTableView, "MergedDesc", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(domainTableView, "FieldType", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(domainTableView, "MergePolicy", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(domainTableView, "SplitPolicy", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(domainTableView, "DomainVal", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(domainTableView, "DomainAltVal", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")

        cursorMDB = arcpy.da.InsertCursor(domainTableView,("DomainName", "DomainType", "DomainRange", "MergedDesc", "FieldType", "MergePolicy", "SplitPolicy", "DomainVal", "DomainAltVal"))

        GDBname = os.path.basename(NoGeomNet)

        target_gdb = NoGeomNet
        arcpy.env.workspace = target_gdb

        time6s = datetime.datetime.now()
        domains = arcpy.da.ListDomains()
        for domain in domains:
            if domain.domainType == 'CodedValue':
                addLog("\tCodedValue:  " + domain.name)
                if domain.name.upper() == "SITECODE":
                    cursorMDB.insertRow((domain.name, domain.domainType, str(domain.range), domain.description, domain.type, domain.mergePolicy, domain.splitPolicy, "", ""))
                for val, desc in domain.codedValues.iteritems():
                    cursorMDB.insertRow((domain.name, domain.domainType, str(domain.range), domain.description, domain.type, domain.mergePolicy, domain.splitPolicy, val, desc))
                    
            elif domain.domainType == 'Range':
                addLog("\tRange:  " + domain.name)
                cursorMDB.insertRow((domain.name, domain.domainType, str(domain.range), domain.description, domain.type, domain.mergePolicy, domain.splitPolicy, "None", "None"))

        del cursorMDB
        arcpy.Delete_management(domainTableView)
        time6e = datetime.datetime.now()
        addLog("Domain Processing Time: " + str((time6e-domainTime)))

    ####################
    ##  Subtypes_All  ##
    ####################

    if runSubtypes_All == "Yes":

        # Output database and tables
        infoGDBname = "schemaInfo_PDM_" + dFolderDate
        if not arcpy.Exists(workingDIR + "\\" + infoGDBname + ".mdb"):
            arcpy.CreatePersonalGDB_management(workingDIR, infoGDBname, "CURRENT")
        infoGDB = workingDIR + "\\" + infoGDBname + ".mdb"

        SubtypeTime = datetime.datetime.now()

        sourceNameTable = infoGDB + "\\" + "Subtypes_All"
        if arcpy.Exists(sourceNameTable):
            arcpy.Delete_management(sourceNameTable)
            arcpy.CreateTable_management(infoGDB, "Subtypes_All", "", "")
        else:
            arcpy.CreateTable_management(infoGDB, "Subtypes_All", "", "")

        subtypeView = "subtypeView"
        arcpy.MakeTableView_management(infoGDB + "\\Subtypes_All", subtypeView)

        addLog("\nCreating " + "Subtypes_All Table")

        arcpy.AddField_management(subtypeView, "FDS_or_Root", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(subtypeView, "SourceName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(subtypeView, "SubtypeField", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(subtypeView, "subtypeDefault", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(subtypeView, "Code", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(subtypeView, "Description", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(subtypeView, "DefaultAttributeName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(subtypeView, "DefaultValue", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(subtypeView, "AttributeConstraintAlternateName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")

        cursorMDB = arcpy.da.InsertCursor(subtypeView,("FDS_or_Root", "SourceName", "SubtypeField",
                                                       "subtypeDefault", "Code", "Description", "DefaultAttributeName",
                                                       "DefaultValue", "AttributeConstraintAlternateName"))

        GDBname = os.path.basename(NoGeomNet)

        arcpy.env.workspace = NoGeomNet

        time10s = datetime.datetime.now()

        for fds in arcpy.ListDatasets('','Feature') + ['']:
            if len(str(fds)) == 0:
                tableList = arcpy.ListTables()
                ##  Tables on Root of GDB
                for table in tableList:
                    
                    # If in SDE check
                    try:
                        fcSplit = (table.split("."))[2]
                    except:
                        fcSplit = table

                    desc = arcpy.Describe(table)
                    if desc.dataType == "Table":

                        desc_lu = arcpy.da.ListSubtypes(table)
                        for stcode, stdict in desc_lu.iteritems():
                            Code = stcode
                            if not stcode == 0:
                                addLog(('{0} | {1} | {2}'.format("Root", table, Code)))
                                Code = stcode
                                for stkey in stdict.iterkeys():
                                    if stkey == "Default":
                                        DefaultSubtype = stdict[stkey]
                                    if stkey == "Name":
                                        Description = stdict[stkey]
                                    if stkey == "SubtypeField":
                                        SubtypeField = stdict[stkey]
                                    if stkey == 'FieldValues':
                                        fields = stdict[stkey]
                                        for field, fieldvals in fields.iteritems():
                                            DomainName = ""
                                            if not field == "":
                                                FieldName = field
                                            if not fieldvals[0] == "":
                                                FieldDefaultValue = fieldvals[0]
                                            if not fieldvals[1] is None:
                                                if not fieldvals[1].name == "":
                                                    FieldDomainName = fieldvals[1].name
                                            else:
                                                FieldDomainName = ""
                                            cursorMDB.insertRow(("Root", fcSplit, SubtypeField, DefaultSubtype, Code, Description, FieldName, FieldDefaultValue, FieldDomainName))

                ## Feature Classes on Root of GDB
                for fc in arcpy.ListFeatureClasses('',''):
                    
                    # If in SDE check
                    try:
                        fcSplit = (fc.split("."))[2]
                    except:
                        fcSplit = fc

                    desc = arcpy.Describe(fc)
                    if desc.dataType == "FeatureClass":

                        desc_lu = arcpy.da.ListSubtypes(fc)
                        for stcode, stdict in desc_lu.iteritems():
                            Code = stcode
                            if not stcode == 0:
                                addLog(('{0} | {1} | {2}'.format("Root", fc, Code)))
                                Code = stcode
                                for stkey in stdict.iterkeys():
                                    if stkey == "Default":
                                        DefaultSubtype = stdict[stkey]
                                    if stkey == "Name":
                                        Description = stdict[stkey]
                                    if stkey == "SubtypeField":
                                        SubtypeField = stdict[stkey]
                                    if stkey == 'FieldValues':
                                        fields = stdict[stkey]
                                        for field, fieldvals in fields.iteritems():
                                            DomainName = ""
                                            if not field == "":
                                                FieldName = field
                                            if not fieldvals[0] == "":
                                                FieldDefaultValue = fieldvals[0]
                                            if not fieldvals[1] is None:
                                                if not fieldvals[1].name == "":
                                                    FieldDomainName = fieldvals[1].name
                                            else:
                                                FieldDomainName = ""
                                            cursorMDB.insertRow(("Root", fcSplit, SubtypeField, DefaultSubtype, Code, Description, FieldName, FieldDefaultValue, FieldDomainName))

            else:
                ## Feature Classes inside Feature Datasets
                for fc in arcpy.ListFeatureClasses('','',fds):

                    # If in SDE check
                    try:
                        fcSplit = (fc.split("."))[2]
                        fdsSplit = (fds.split("."))[2]
                    except:
                        fcSplit = fc
                        fdsSplit = fds

                    desc = arcpy.Describe(fc)
                    if desc.dataType == "FeatureClass":

                        desc_lu = arcpy.da.ListSubtypes(fc)
                        for stcode, stdict in desc_lu.iteritems():
                            Code = stcode
                            if not stcode == 0:
                                addLog(('{0} | {1} | {2}'.format(fds, fc, Code)))
                                Code = stcode
                                for stkey in stdict.iterkeys():
                                    if stkey == "Default":
                                        DefaultSubtype = stdict[stkey]
                                    if stkey == "Name":
                                        Description = stdict[stkey]
                                    if stkey == "SubtypeField":
                                        SubtypeField = stdict[stkey]
                                    if stkey == 'FieldValues':
                                        fields = stdict[stkey]
                                        for field, fieldvals in fields.iteritems():
                                            DomainName = ""
                                            if not field == "":
                                                FieldName = field
                                            if not fieldvals[0] == "":
                                                FieldDefaultValue = fieldvals[0]
                                            if not fieldvals[1] is None:
                                                if not fieldvals[1].name == "":
                                                    FieldDomainName = fieldvals[1].name
                                            else:
                                                FieldDomainName = ""
                                            cursorMDB.insertRow((fdsSplit, fcSplit, SubtypeField, DefaultSubtype, Code, Description, FieldName, FieldDefaultValue, FieldDomainName))

        del cursorMDB
        arcpy.Delete_management(subtypeView)

        time10e = datetime.datetime.now()
        addLog("Subtype_All Processing Time: " + str((time10e-SubtypeTime)))

    #####################
    ##  Relationships  ##
    #####################

    if runRelationships == "Yes":

        addLog("\nExporting Relationship Table")

        # Output database and tables
        infoGDBname = "schemaInfo_PDM_" + dFolderDate
        if not arcpy.Exists(workingDIR + "\\" + infoGDBname + ".mdb"):
            arcpy.CreatePersonalGDB_management(workingDIR, infoGDBname, "CURRENT")
        infoGDB = workingDIR + "\\" + infoGDBname + ".mdb"

        relStartTime = datetime.datetime.now()

        sourceNameTable = infoGDB + "\\" + "Relationships"
        if arcpy.Exists(sourceNameTable):
            arcpy.Delete_management(sourceNameTable)
            arcpy.CreateTable_management(infoGDB, "Relationships", "", "")
        else:
            arcpy.CreateTable_management(infoGDB, "Relationships", "", "")

        relTableView = "relTableView"
        arcpy.MakeTableView_management(infoGDB + "\\Relationships", relTableView)
        sourceNameTable = relTableView

        arcpy.AddField_management(sourceNameTable, "Name", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "FDS_or_Root", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "BackwardPathLabel", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "Cardinality", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "ClassKey", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "DestinationClassName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "ForwardPathLabel", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "AttachmentRelationship", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "Attributed", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "Composite", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "Reflexive", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "KeyType", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "Notification", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "OriginClassName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "oPrimaryKey", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "oForeignKey", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "dPrimaryKey", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "dForeignKey", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        
        GDBname = os.path.basename(NoGeomNet)

        target_gdb = NoGeomNet
        arcpy.env.workspace = target_gdb
        descRel = arcpy.Describe(target_gdb)

        time7s = datetime.datetime.now()

        relFields = ("Name", "FDS_or_Root", "BackwardPathLabel", "Cardinality", "ClassKey",
                     "DestinationClassName", "ForwardPathLabel", "AttachmentRelationship",
                     "Attributed", "Composite", "Reflexive", "KeyType", "Notification",
                     "OriginClassName", "oPrimaryKey", "oForeignKey", "dPrimaryKey", "dForeignKey")
        with arcpy.da.InsertCursor(sourceNameTable, relFields) as cursorRel:
            
            for child in descRel.children:

                if child.dataType == "RelationshipClass":
                    childName = child.name

                    dcn = str(child.destinationClassNames)
                    dcn = dcn.replace("[u'","").replace("']","").replace("\"","!")
                    ocn = str(child.originClassNames)
                    ocn = ocn.replace("[u'","").replace("']","").replace("\"","!")

                    ock = str(child.originClassKeys)
##                    print "ock: " + ock
##                    ock = ock.replace("[","").replace("]","").replace("(","").replace(")","").replace("'","").replace(" ","").replace("u","").replace(",,",",")
                    ock = ock.replace("[(u'","").replace("', u'",",").replace("'), (u'",",").replace("')]","").replace(",,",",")
##                    print "ock: " + ock
                    oPrimaryKey = (ock.split(","))[1]
                    oPrimaryKeyVal = (ock.split(","))[0]
                    oForeignKey = (ock.split(","))[3]
                    oForeignKeyVal = (ock.split(","))[2]

                    dck = str(child.destinationClassKeys)
##                    print "dck: " + dck
                    dck = dck.replace("[(u'","").replace("', u'",",").replace("'), (u'",",").replace("')]","").replace(",,",",").replace("[]","")
##                    print "dck: " + dck
##                    dck = dck.replace("[","").replace("]","").replace("(","").replace(")","").replace("'","").replace(" ","").replace("u","").replace(",,",",")
                    if not dck == "":
                        dPrimaryKey = (dck.split(","))[1]
                        dPrimaryKeyVal = (dck.split(","))[0]
                        dForeignKey = (dck.split(","))[3]
                        dForeignKeyVal = (dck.split(","))[2]
                    else:
                        dPrimaryKeyVal = ""
                        dForeignKeyVal = ""

                    if workspace_type == "SDE":
                        childN = (childName.split("."))[2]
                        childD = (dcn.split("."))[2]
                        childO = (ocn.split("."))[2]
                    else:
                        childN = child.name
                        childD = dcn
                        childO = ocn

                    addLog("\tRelationship:  " + childN)

                    cursorRel.insertRow((childN, "Root", child.backwardPathLabel, child.cardinality,
                                         child.classKey, childD, child.forwardPathLabel,
                                         str(child.isAttachmentRelationship), str(child.isAttributed),
                                         str(child.isComposite), str(child.isReflexive), child.keyType,
                                         child.notification, childO, oPrimaryKeyVal, oForeignKeyVal, dPrimaryKeyVal, dForeignKeyVal))

            ## Feature Classes inside Feature Datasets  
            for fds in arcpy.ListDatasets('','Feature'):
                descRelFDS = arcpy.Describe(fds)
                for childFDS in descRelFDS.children:
                    if childFDS.dataType == "RelationshipClass":

                        childFDSName = childFDS.name

                        try:
                            childN = (childFDSName.split("."))[2]
                            fdsSplit = (fds.split("."))[2]
                        except:
                            childN = childFDS.name
                            fdsSplit = fds

                        addLog("\tRelationship:  " + fdsSplit + "\\" + childN)
                        
                        dcnFDS = str(childFDS.destinationClassNames)
                        dcnFDS = dcnFDS.replace("[u'","").replace("']","").replace("\"","!")
                        ocnFDS = str(childFDS.originClassNames)
                        ocnFDS = ocnFDS.replace("[u'","").replace("']","").replace("\"","!")
                        
                        ockFDS = str(childFDS.originClassKeys)
                        ockFDS = ockFDS.replace("[(u'","").replace("', u'",",").replace("'), (u'",",").replace("')]","").replace(",,",",")
##                        addLog("\nockFDS: " + ockFDS)
##                        ockFDS = ockFDS.replace("[","").replace("]","").replace("(","").replace(")","").replace("'","").replace(" ","").replace("u","").replace(",,",",")
                        oPrimaryKey = (ockFDS.split(","))[1]
                        oPrimaryKeyVal = (ockFDS.split(","))[0]
                        oForeignKey = (ockFDS.split(","))[3]
                        oForeignKeyVal = (ockFDS.split(","))[2]

                        dckFDS = str(childFDS.destinationClassKeys)
                        dckFDS = dckFDS.replace("[(u'","").replace("', u'",",").replace("'), (u'",",").replace("')]","").replace(",,",",").replace("[]","")
##                        addLog("\ndckFDS: " + dckFDS)
##                        dckFDS = dckFDS.replace("[","").replace("]","").replace("(","").replace(")","").replace("'","").replace(" ","").replace("u","").replace(",,",",")
                        if not dckFDS == "":
                            dPrimaryKey = (dckFDS.split(","))[1]
                            dPrimaryKeyVal = (dckFDS.split(","))[0]
                            dForeignKey = (dckFDS.split(","))[3]
                            dForeignKeyVal = (dckFDS.split(","))[2]
                        else:
                            dPrimaryKeyVal = ""
                            dForeignKeyVal = ""

                        try:
                            childD = (dcnFDS.split("."))[2]
                            childO = (ocnFDS.split("."))[2]
                        except:
                            childD = dcnFDS
                            childO = ocnFDS

                        cursorRel.insertRow((childN, fdsSplit, childFDS.backwardPathLabel, childFDS.cardinality,
                                             childFDS.classKey, childD, childFDS.forwardPathLabel,
                                             str(childFDS.isAttachmentRelationship), str(childFDS.isAttributed),
                                             str(childFDS.isComposite), str(childFDS.isReflexive),
                                             childFDS.keyType, childFDS.notification, childO,
                                             oPrimaryKeyVal, oForeignKeyVal, dPrimaryKeyVal, dForeignKeyVal))

        del cursorRel
        arcpy.Delete_management(relTableView)
        addLog("Relationship Processing Time: " + str((datetime.datetime.now()-relStartTime)))

    ################################
    ##  Relationships Attributes  ##
    ################################

    if runRelationshipsAtt == "Yes":

        addLog("\nExporting Relationship Attribute Table")

        # Output database and tables
        infoGDBname = "schemaInfo_PDM_" + dFolderDate
        if not arcpy.Exists(workingDIR + "\\" + infoGDBname + ".mdb"):
            arcpy.CreatePersonalGDB_management(workingDIR, infoGDBname, "CURRENT")
        infoGDB = workingDIR + "\\" + infoGDBname + ".mdb"

        relStartTime = datetime.datetime.now()

        relAtt = "Relationships_Att"
        if arcpy.Exists(infoGDB + "\\" + relAtt):
            arcpy.Delete_management(infoGDB + "\\" + relAtt)
            arcpy.CreateTable_management(infoGDB, relAtt, "", "")
        else:
            arcpy.CreateTable_management(infoGDB, relAtt, "", "")
        relAttTable = infoGDB + "\\" + relAtt

        relAttTableView = "relAttTableView"
        arcpy.MakeTableView_management(relAttTable, relAttTableView)

        arcpy.AddField_management(relAttTableView, "FDS_or_Root", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(relAttTableView, "SourceName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(relAttTableView, "FieldName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(relAttTableView, "FieldType", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(relAttTableView, "FieldLength", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")

        arcpy.env.workspace = NoGeomNet
        descAttRel = arcpy.Describe(NoGeomNet)
            
        time7s = datetime.datetime.now()
        
        relAttFields = ("FDS_or_Root","SourceName","FieldName","FieldType","FieldLength")
        with arcpy.da.InsertCursor(relAttTableView, relAttFields) as cursorRelAttTable:
            for childAtt in descAttRel.children:
                if childAtt.dataType == "RelationshipClass":

                    childAttName = childAtt.name
                    
                    if str(childAtt.isAttributed) == "True":

                        addLog("\tRelationshipAtt:  " + "Root\\" + childN)

                        oName,dName = childAttName.split("_")
                        oNameSDSID = oName + "SDSID"
                        dNameSDSID = dName + "SDSID"

                        attChildAtt = NoGeomNet + "\\" + childAttName
                        attDesc = arcpy.Describe(attChildAtt)
                        fieldList = arcpy.ListFields(attChildAtt)

                        for field in fieldList:

                            if field.name.upper() == 'OBJECTID':continue
                            if field.name.upper().startswith("SHAPE"): continue
                            if field.name.upper() == ("RID"): continue
                            if field.name.upper() == ("GLOBALID"): continue
                            if field.name.upper() == (oNameSDSID.upper()): continue
                            if field.name.upper() == (dNameSDSID.upper()): continue
                            
                            if field.type == "Integer":
                                fieldLength = ""
                            else:
                                fieldLength = str(field.length)
                            
                            cursorRelAttTable.insertRow(("Root",childAttName,field.name,field.type,fieldLength))
                            
            ## Feature Classes inside Feature Datasets  
            for fds in arcpy.ListDatasets('','Feature'):
                descRelFDS = arcpy.Describe(fds)
                for childFDS in descRelFDS.children:
                    if childFDS.dataType == "RelationshipClass":

                        childFDSName = childFDS.name

                        try:
                            childN = (childFDSName.split("."))[2]
                            fdsSplit = (fds.split("."))[2]
                        except:
                            childN = childFDS.name
                            fdsSplit = fds
                        
                        if str(childFDS.isAttributed) == "True":

                            addLog("\tRelationshipAtt:  " + fdsSplit + "\\" + childN)

                            oName,dName = childFDSName.split("_")
                            oNameSDSID = oName + "SDSID"
                            dNameSDSID = dName + "SDSID"

                            attFDSchild = NoGeomNet + "\\" + fdsSplit + "\\" + childFDSName
                            attFDSdesc = arcpy.Describe(attFDSchild)
                            fieldList = arcpy.ListFields(attFDSchild)

                            fieldList = arcpy.ListFields(NoGeomNet + "\\" + fdsSplit + "\\" + childFDSName)

                            for field in fieldList:

                                if field.name.upper() == 'OBJECTID':continue
                                if field.name.upper().startswith("SHAPE"): continue
                                if field.name.upper() == ("RID"): continue
                                if field.name.upper() == ("GLOBALID"): continue
                                if field.name.upper() == (oNameSDSID.upper()): continue
                                if field.name.upper() == (dNameSDSID.upper()): continue

                                if field.type == "Integer":
                                    fieldLength = ""
                                else:
                                    fieldLength = str(field.length)

                                cursorRelAttTable.insertRow((fdsSplit, childFDSName, field.name,
                                                             field.type, fieldLength))
        del cursorRelAttTable
        arcpy.Delete_management(relAttTableView)
        addLog("Relationship Attribute Processing Time: " + str((datetime.datetime.now()-relStartTime)))
        
    ##########################
    ##  Geometric Networks  ##
    ##########################

    if runGeometricNetwork == "Yes":

        import subprocess

        ## Looking for GetGeometricNetworkDetails.exe in same folder as Schema.py
        aoCommand = os.path.join(os.path.dirname('__file__'),r"GetGeometricNetworkDetails.exe")

        # Output database and tables
        infoGDBname = "schemaInfo_PDM_" + dFolderDate
        if not arcpy.Exists(workingDIR + "\\" + infoGDBname + ".mdb"):
            arcpy.CreatePersonalGDB_management(workingDIR, infoGDBname, "CURRENT")
        infoGDB = workingDIR + "\\" + infoGDBname + ".mdb"

        gnStartTime = datetime.datetime.now()

        sourceNameTable = infoGDB + "\\" + "GeometricNetworks"
        if arcpy.Exists(sourceNameTable):
            arcpy.Delete_management(sourceNameTable)
            arcpy.CreateTable_management(infoGDB, "GeometricNetworks", "", "")
        else:
            arcpy.CreateTable_management(infoGDB, "GeometricNetworks", "", "")

        gnTableView = "gnTableView"
        arcpy.MakeTableView_management(infoGDB + "\\GeometricNetworks", gnTableView)

        addLog("\n\nExporting Geometric Networks Table")

        arcpy.AddField_management(gnTableView, "FDS_or_Root", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(gnTableView, "Name", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(gnTableView, "NetworkType", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(gnTableView, "OrphanFCname", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(gnTableView, "FCname", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(gnTableView, "Role", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(gnTableView, "SourcesSinks", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")

        cursorGN = arcpy.da.InsertCursor(sourceNameTable,("FDS_or_Root", "Name", "NetworkType", "OrphanFCname", "FCname", "Role", "SourcesSinks"))

        for dirpath, dirnames, filenames in arcpy.da.Walk(GeomNet, datatype=['GeometricNetwork']):
            for filename in filenames:

                FDSpath = os.path.dirname(os.path.join(dirpath, filename))
                FDS = os.path.basename(FDSpath)
                
                addLog("\n" + FDS + " | " + filename)

                gn = os.path.join(dirpath, filename)
                
                desc = arcpy.Describe(gn)
                for fcname in desc.featureClassNames:
                    if fcname.endswith("_Junctions"): continue
                    addLog("\t" + fcname)
                    pOutput = subprocess.Popen([aoCommand, GeomNet, FDS,filename,fcname],stdout=subprocess.PIPE,creationflags=0x08000000)
                    outputString = pOutput.communicate()[0]
                    if ";" not in outputString:
                        raise Exception("GN CommandLine Error: " + outputString)
                    SourcesSink,Role = outputString.split(";")
                    cursorGN.insertRow((FDS, filename, desc.networkType, desc.orphanJunctionFeatureClassName, fcname, Role, SourcesSink))
                    
        del cursorGN
        addLog("Geometric Network Processing Time: " + str((datetime.datetime.now()-gnStartTime)))

    #########################
    ##  Metadata Exporter  ##
    #########################

    if runMetadataExporter == "Yes":

        import xml.dom.minidom
        from xml.etree import ElementTree
        from xml.etree.ElementTree import Element
        from xml.etree.ElementTree import SubElement
        import xml.etree.ElementTree as ET

        # Output database and tables
        infoGDBname = "schemaInfo_PDM_" + dFolderDate
        if not arcpy.Exists(workingDIR + "\\" + infoGDBname + ".mdb"):
            arcpy.CreatePersonalGDB_management(workingDIR, infoGDBname, "CURRENT")
        infoGDB = workingDIR + "\\" + infoGDBname + ".mdb"

        gnStartTime = datetime.datetime.now()

        addLog("\nExporting Metadata")
        
        metaE_s = datetime.datetime.now()

        inMetadata = workingDIR + "\\" + "inMetadata"
        if not os.path.exists(inMetadata): os.makedirs(inMetadata)

        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = NoGeomNet

        now = datetime.datetime.now()

        dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
        translator = dir + "Metadata/Translator/ARCGIS2FGDC.xml"

        GDBname = os.path.basename(NoGeomNet)

        sourceNameTable = infoGDB + "\\" + "UpdatedMetadata"
        if arcpy.Exists(sourceNameTable):
            arcpy.Delete_management(sourceNameTable)
            arcpy.CreateTable_management(infoGDB, "UpdatedMetadata", "", "")
        else:
            arcpy.CreateTable_management(infoGDB, "UpdatedMetadata", "", "")

        metadataTableView = "metadataTableView"
        arcpy.MakeTableView_management(infoGDB + "\\UpdatedMetadata", metadataTableView)
        sourceNameTable = metadataTableView

        arcpy.AddField_management(sourceNameTable, "FDS_or_Root", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "FCname", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "Description", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "AttName", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "AttDesc", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "DomainAltVal", "TEXT", "", "", "255", "", "NULLABLE", "NON_REQUIRED", "")
        arcpy.AddField_management(sourceNameTable, "DomainAltValDesc", "TEXT", "", "", "1000", "", "NULLABLE", "NON_REQUIRED", "")

        cursorMDB = arcpy.da.InsertCursor(sourceNameTable,("FDS_or_Root","FCname","Description","AttName","AttDesc","DomainAltVal","DomainAltValDesc"))

        for fds in arcpy.ListDatasets('','Feature') + ['']:
            
            if len(str(fds)) == 0:
                
                ## Table on Root of GDB
                tableList = arcpy.ListTables()
                for table in tableList:

                    fds = "Root"

                    fdsfcTime = datetime.datetime.now()

                    xmlfileFC = (inMetadata + "\\" + table + ".xml")
                    addLog(fds + " | Table | " + table)
                    arcpy.ExportMetadata_conversion(table, translator, xmlfileFC)

                    ## Exporting Metadata attributes ##
                    tree = ET.parse(xmlfileFC)

                    root = tree.getroot()

                    for checkD in root.iter('attr'):
                        if root.find('idinfo/descript/abstract') is None:
                            arcpy.UpgradeMetadata_conversion (table, "FGDC_TO_ARCGIS")
                            arcpy.ExportMetadata_conversion(table, translator, xmlfileFC)

                    edomList = []
                    del edomList[:]
                    for child in root.iter('attr'):
                        
                        name = child.find('attrlabl').text

                        if child.find('attrdef') is None:
                            descDef = ''
                        else:
                            descDef = child.find('attrdef').text
                            
                        abstract = root.find('idinfo/descript/abstract').text
                        enttypl = root.find('eainfo/detailed/enttyp/enttypl').text

                        if name.upper().startswith('SHAPE'):continue
##                        if name.upper() == 'GLOBALID':continue
                        if name.upper() == 'OBJECTID':continue

                        for e in child.getiterator():
                            if e.tag == 'edom':
                                edomList.append(name)

                        newList = set(edomList)
                        if name in newList:
                            for e in child.getiterator():
                                if e.tag == 'edom':
                                    edomList.append(name)
                                    edomv = e.find('edomv').text

                                    if e.find('edomvd') is None:
                                        edomvd = ''
                                    else:
                                        edomvd = e.find('edomvd').text
                                        
                                    cursorMDB.insertRow((fds,enttypl,abstract,name,descDef,edomv,edomvd))
                        else:
                            cursorMDB.insertRow((fds,enttypl,abstract,name,descDef,'',''))
                            
                ## Feature Classes on Root of GDB
                for fc in arcpy.ListFeatureClasses('',''):

                    fds = "Root"

                    fdsfcTime = datetime.datetime.now()

                    xmlfileFC = (inMetadata + "\\" + fc + ".xml")
                    addLog(fds + " | FC | " + fc)
                    arcpy.ExportMetadata_conversion(fc, translator, xmlfileFC)

                    ## Exporting Metadata attributes ##
                    tree = ET.parse(xmlfileFC)

                    root = tree.getroot()

                    for checkD in root.iter('attr'):
                        if root.find('idinfo/descript/abstract') is None:
                            arcpy.UpgradeMetadata_conversion (fc, "FGDC_TO_ARCGIS")
                            arcpy.ExportMetadata_conversion(fc, translator, xmlfileFC)

                    edomList = []
                    del edomList[:]
                    for child in root.iter('attr'):
                        
                        name = child.find('attrlabl').text

                        if child.find('attrdef') is None:
                            descDef = ''
                        else:
                            descDef = child.find('attrdef').text
                            
                        abstract = root.find('idinfo/descript/abstract').text
                        enttypl = root.find('eainfo/detailed/enttyp/enttypl').text

                        if name.upper().startswith('SHAPE'):continue
##                        if name.upper() == 'GLOBALID':continue
                        if name.upper() == 'OBJECTID':continue

                        for e in child.getiterator():
                            if e.tag == 'edom':
                                edomList.append(name)

                        newList = set(edomList)
                        if name in newList:
                            for e in child.getiterator():
                                if e.tag == 'edom':
                                    edomList.append(name)
                                    edomv = e.find('edomv').text

                                    if e.find('edomvd') is None:
                                        edomvd = ''
                                    else:
                                        edomvd = e.find('edomvd').text
                                        
                                    cursorMDB.insertRow((fds,enttypl,abstract,name,descDef,edomv,edomvd))
                        else:
                            cursorMDB.insertRow((fds,enttypl,abstract,name,descDef,'',''))
            else:

                ## Feature Classes in FDS
                for fc in arcpy.ListFeatureClasses('','',fds):

                    if not fc[-4:] == "Anno":

                        fdsfcTime = datetime.datetime.now()

                        xmlfileFC = (inMetadata + "\\" + fc + ".xml")
                        addLog(fds + " | FC | " + fc)
                        arcpy.ExportMetadata_conversion(fc, translator, xmlfileFC)

                        ## Exporting Metadata attributes ##
                        tree = ET.parse(xmlfileFC)

                        root = tree.getroot()

                        for checkD in root.iter('attr'):
                            if root.find('idinfo/descript/abstract') is None:
                                arcpy.UpgradeMetadata_conversion (fc, "FGDC_TO_ARCGIS")
                                arcpy.ExportMetadata_conversion(fc, translator, xmlfileFC)

                        edomList = []
                        del edomList[:]
                        for child in root.iter('attr'):
                            
                            name = child.find('attrlabl').text
                            abstract = root.find('idinfo/descript/abstract').text
                            enttypl = root.find('eainfo/detailed/enttyp/enttypl').text

                            if name.upper().startswith('SHAPE'):continue
    ##                        if name.upper() == 'GLOBALID':continue
                            if name.upper() == 'OBJECTID':continue

                            if child.find('attrdef') is None:
                                descDef = ''
                            else:
                                descDef = child.find('attrdef').text

                            for e in child.getiterator():
                                if e.tag == 'edom':
                                    edomList.append(name)

                            newList = set(edomList)
                            if name in newList:
                                for e in child.getiterator():
                                    if e.tag == 'edom':
                                        edomList.append(name)
                                        edomv = e.find('edomv').text

                                        if e.find('edomvd') is None:
                                            edomvd = ''
                                        else:
                                            edomvd = e.find('edomvd').text
                                            
                                        cursorMDB.insertRow((fds,enttypl,abstract,name,descDef,edomv,edomvd))
                            else:
                                cursorMDB.insertRow((fds,enttypl,abstract,name,descDef,'',''))
        del cursorMDB
        arcpy.Delete_management(metadataTableView)
        addLog("Metadata Processing Time: " + str((datetime.datetime.now()-metaE_s)))
    addLog("\nTotal Processing Time: " + str((datetime.datetime.now()-totalStartTime)))
    
except Exception, e:

    # If an error occurred, print line number and error message
    import traceback, sys
    tb = sys.exc_info()[2]
    addLog("\nLine %i" % tb.tb_lineno)
    addLog(e.message)
    addLog("Total Processing Time: " + str((datetime.datetime.now()-startTime)))

    ## Email that script has stopped.
    sys.path.append(r"C:\Workspace\Personal\Secret")
    from secrets import gmail
    import tools_v2

    if __name__ == "__main__":
        email = gmail["email"]
        password = gmail["password"]

    scriptName = "Step_04"
    tools_v2.SendErrorGmail(email, password, tb, e, scriptName)


