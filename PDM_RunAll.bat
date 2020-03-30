@echo off

set Version=20190529
set Vnum=Navy_4_1_Utilities
set LDMversion=LDM_4_0
set PDMname=PDM40
set pFolder=M:\Projects\SchemaInfo

:: What to process in LDM_to_PDM script.
set runDomains=Yes
set runFCtables=Yes
set runShapeSort=Yes
set runSubtypes=Yes
set runRel=Yes
set runRelAtt=Yes
set runDefaultValue=Yes
set runMetadata=Yes
set runGeoNet=Nooooope

:: What to process in Schema script.
set Schema_LDMtoPDM=Yes
set Schema_runSourceSchema=Yes
set Schema_runDomains=Yes
set Schema_runSubtypes_All=Yes
set Schema_runRelationships=Yes
set Schema_runRelationshipsAtt=Yes
set Schema_runGeometricNetwork=Yes
set Schema_runMetadataExporter=Yes

echo %pFolder%

cd %pFolder%

:: Run in python 32bit mode
:: C:\Python27\ArcGIS10.5\python.exe Step01_LDM_to_PDM_Bat.py %1 %Version% %Vnum% %LDMversion% %PDMname% %pFolder% %runDomains% %runFCtables% %runShapeSort% %runSubtypes% %runRel% %runRelAtt% %runDefaultValue% %runMetadata% %runGeoNet%

:: C:\Python27\ArcGIS10.5\python.exe Step02_SDEtoFGDB_Bat.py %1 %Version% %Vnum% %LDMversion% %PDMname% %pFolder%

:: C:\Python27\ArcGIS10.5\python.exe Step03_PDM_addDomains_Bat.py %1 %Version% %Vnum% %LDMversion% %PDMname% %pFolder%

C:\Python27\ArcGIS10.5\python.exe Step04_Schema_Bat.py %1 %Version% %Vnum% %LDMversion% %PDMname% %pFolder% %Schema_LDMtoPDM% %Schema_runSourceSchema% %Schema_runDomains% %Schema_runSubtypes_All% %Schema_runRelationships% %Schema_runRelationshipsAtt% %Schema_runGeometricNetwork% %Schema_runMetadataExporter%

:: C:\Python27\ArcGIS10.5\python.exe Step05_SendEmail_Bat.py %1 %Version% %Vnum% %LDMversion% %PDMname% %pFolder%

pause

:: --------------------------------------------------------
:PadHour
Set  Hour=%*
If %Hour% GEQ 10 then Goto :EOF
Set Hour=0%Hour%
goto :EOF