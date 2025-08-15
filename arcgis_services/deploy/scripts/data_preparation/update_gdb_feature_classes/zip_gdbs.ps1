# Zip up Perils/NonEditLayers file geodatabases 

# Functions 

# Perils gdb is very large and doesn't compress well - copy duplicate instead? 

# Logic

# TEST

# $test_source = "C:\Users\F33124\Documents\release 2023.1\test\ziptest\fakegdb.gdb"
# $test_archive = "C:\Users\F33124\Documents\release 2023.1\test\ziptest\fakegdb"
# Compress-Archive -LiteralPath $test_source -DestinationPath $test_archive

# # NON_EDIT_LAYERS 

# $noneditlayers_source = "D:\esriuk\FGDB\NON_EDIT_LAYERS_A.gdb"
# $noneditlayers_archive = "D:\esriuk\FGDB\NON_EDIT_LAYERS_A"
# Compress-Archive -LiteralPath $noneditlayers_source -DestinationPath $noneditlayers_archive

# PERILS 

$perils_source = "D:\esriuk\FGDB\PERILS_A.gdb"
$perils_archive = "D:\esriuk\FGDB\PERILS_A"
Compress-Archive -LiteralPath $perils_source -DestinationPath $perils_archive