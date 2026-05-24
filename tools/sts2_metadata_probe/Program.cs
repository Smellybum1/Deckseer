using System.Reflection.Metadata;
using System.Reflection.PortableExecutable;
using System.Text.RegularExpressions;

if (args.Length < 1)
{
    Console.Error.WriteLine("Usage: dotnet run --project tools/sts2_metadata_probe -- <assembly_path> [regex]");
    return 2;
}

string assemblyPath = args[0];
string pattern = args.Length > 1 ? args[1] : ".";
Regex regex = new(pattern, RegexOptions.IgnoreCase | RegexOptions.CultureInvariant);

using FileStream stream = File.OpenRead(assemblyPath);
using PEReader peReader = new(stream);
MetadataReader reader = peReader.GetMetadataReader();

foreach (TypeDefinitionHandle typeHandle in reader.TypeDefinitions)
{
    TypeDefinition type = reader.GetTypeDefinition(typeHandle);
    string typeName = TypeName(reader, type);
    List<string> members = [];
    bool typeMatches = regex.IsMatch(typeName);

    foreach (FieldDefinitionHandle fieldHandle in type.GetFields())
    {
        FieldDefinition field = reader.GetFieldDefinition(fieldHandle);
        string fieldName = reader.GetString(field.Name);
        if (typeMatches || regex.IsMatch(fieldName))
        {
            members.Add($"  field {fieldName}");
        }
    }

    foreach (PropertyDefinitionHandle propertyHandle in type.GetProperties())
    {
        PropertyDefinition property = reader.GetPropertyDefinition(propertyHandle);
        string propertyName = reader.GetString(property.Name);
        if (typeMatches || regex.IsMatch(propertyName))
        {
            members.Add($"  property {propertyName}");
        }
    }

    foreach (MethodDefinitionHandle methodHandle in type.GetMethods())
    {
        MethodDefinition method = reader.GetMethodDefinition(methodHandle);
        string methodName = reader.GetString(method.Name);
        if (typeMatches || regex.IsMatch(methodName))
        {
            members.Add($"  method {methodName}");
        }
    }

    if (typeMatches || members.Count > 0)
    {
        Console.WriteLine(typeName);
        foreach (string member in members)
        {
            Console.WriteLine(member);
        }
    }
}

return 0;

static string TypeName(MetadataReader reader, TypeDefinition type)
{
    string ns = reader.GetString(type.Namespace);
    string name = reader.GetString(type.Name);
    return string.IsNullOrEmpty(ns) ? name : $"{ns}.{name}";
}
