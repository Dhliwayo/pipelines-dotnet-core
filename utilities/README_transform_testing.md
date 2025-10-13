# XML Configuration Transform Testing

This folder contains utilities to test XML configuration transformations locally before deploying to Azure Pipelines.

## Quick Start

### Test BatchManager Config Transformation

```powershell
# Test PreProd transformation (default)
.\utilities\test_batchmanager_transform.ps1

# Test Production transformation
.\utilities\test_batchmanager_transform.ps1 -Environment Production

# Test Staging transformation
.\utilities\test_batchmanager_transform.ps1 -Environment Staging
```

The script will:
1. Apply the transformation
2. Save output to `staging/config/BatchManager/Web.Transformed.[Environment].config`
3. Prompt you to open the file for review

### Test Any Config Transformation

```powershell
.\utilities\test_transform.ps1 `
    -SourceFile "path\to\source\Web.config" `
    -TransformFile "path\to\transform\Web.Production.config" `
    -OutputFile "path\to\output\Web.Transformed.config"
```

## How It Works

The script uses the **Microsoft.Web.XmlTransform** library (the same library used by Visual Studio and Azure Pipelines) to perform transformations.

### First Run

On first run, the script will automatically:
1. Download the Microsoft.Web.Xdt NuGet package
2. Extract the `Microsoft.Web.XmlTransform.dll`
3. Save it to the `utilities` folder for future use

### Transform File Syntax

Transform files use XML Document Transform (XDT) syntax:

```xml
<?xml version="1.0"?>
<configuration xmlns:xdt="http://schemas.microsoft.com/XML-Document-Transform">
  
  <!-- Transform connectionStrings -->
  <connectionStrings>
    <add name="MyConnection" 
         connectionString="Data Source=PROD-SERVER;..." 
         xdt:Transform="SetAttributes" 
         xdt:Locator="Match(name)"/>
  </connectionStrings>

  <!-- Transform appSettings -->
  <appSettings>
    <add key="Environment" 
         value="Production" 
         xdt:Transform="SetAttributes" 
         xdt:Locator="Match(key)"/>
  </appSettings>
</configuration>
```

### Common Transform Operations

| Operation | Description | Example |
|-----------|-------------|---------|
| `SetAttributes` | Update specific attributes | `xdt:Transform="SetAttributes"` |
| `Insert` | Add new element | `xdt:Transform="Insert"` |
| `InsertIfMissing` | Add only if doesn't exist | `xdt:Transform="InsertIfMissing"` |
| `Remove` | Delete element | `xdt:Transform="Remove"` |
| `Replace` | Replace entire element | `xdt:Transform="Replace"` |
| `RemoveAttributes` | Remove specific attributes | `xdt:Transform="RemoveAttributes(debug)"` |

### Common Locators

| Locator | Description | Example |
|---------|-------------|---------|
| `Match(name)` | Find by name attribute | `xdt:Locator="Match(name)"` |
| `Match(key)` | Find by key attribute | `xdt:Locator="Match(key)"` |
| `Condition(@name='value')` | Find by condition | `xdt:Locator="Condition(@name='MyConnection')"` |

## Verifying Transformations

After running the test script:

1. **Review the output file** - Check that all values were transformed correctly
2. **Compare with source** - Use a diff tool to see what changed
3. **Check token replacement** - Ensure tokens like `#{DB_PASSWORD}#` are in place

### Example Comparison

```powershell
# Use code to compare files
code --diff staging/config/BatchManager/Web.config staging/config/BatchManager/Web.Transformed.PreProd.config
```

## Troubleshooting

### DLL Download Fails

If automatic download fails, manually install:

1. Download: https://www.nuget.org/packages/Microsoft.Web.Xdt/
2. Extract the `.nupkg` file (rename to `.zip` if needed)
3. Copy `Microsoft.Web.XmlTransform.dll` from `lib\netstandard2.0\` to `utilities\` folder

### Transformation Fails

Common issues:
- **Locator not matching**: Ensure your `xdt:Locator` matches the actual attribute in the source file
- **Namespace missing**: Transform file must include `xmlns:xdt="http://schemas.microsoft.com/XML-Document-Transform"`
- **Invalid XML**: Both source and transform files must be valid XML

### Permission Issues

If you get permission errors:
- Run PowerShell as Administrator, or
- Ensure you have write permissions to the output directory

## Integration with Azure Pipeline

The same transforms tested locally will work in your Azure Pipeline. The pipeline uses the `FileTransform` task:

```yaml
- task: FileTransform@1
  inputs:
    folderPath: '$(System.DefaultWorkingDirectory)/**/*.config'
    fileType: 'xml'
    targetFiles: '**/Web.config'
```

## Additional Resources

- [Web.config Transformation Syntax](https://learn.microsoft.com/en-us/aspnet/web-forms/overview/deployment/visual-studio-web-deployment/web-config-transformations)
- [XDT Transform Samples](https://github.com/projectkudu/kudu/wiki/Xdt-transform-samples)
- [Azure Pipeline File Transform Task](https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/file-transform-v1)

