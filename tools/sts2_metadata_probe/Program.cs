using System.Reflection.Metadata;
using System.Reflection.Metadata.Ecma335;
using System.Reflection.PortableExecutable;
using System.Collections.Immutable;
using System.Reflection;
using System.Text.RegularExpressions;

if (args.Length < 1)
{
    Console.Error.WriteLine("Usage: dotnet run --project tools/sts2_metadata_probe -- <assembly_path> [regex]");
    return 2;
}

string assemblyPath = args[0];
string pattern = args.Length > 1 ? args[1] : ".";
bool includeSignatures = args.Contains("--signatures");
bool includeAccessibility = args.Contains("--accessibility");
Regex regex = new(pattern, RegexOptions.IgnoreCase | RegexOptions.CultureInvariant);

using FileStream stream = File.OpenRead(assemblyPath);
using PEReader peReader = new(stream);
MetadataReader reader = peReader.GetMetadataReader();
SignatureTextProvider signatureProvider = new();

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
            string prefix = includeAccessibility ? $"  {FieldAccessibility(field.Attributes)} field" : "  field";
            members.Add($"{prefix} {fieldName}");
        }
    }

    foreach (PropertyDefinitionHandle propertyHandle in type.GetProperties())
    {
        PropertyDefinition property = reader.GetPropertyDefinition(propertyHandle);
        string propertyName = reader.GetString(property.Name);
        if (typeMatches || regex.IsMatch(propertyName))
        {
            string prefix = includeAccessibility ? $"  {PropertyAccessibility(reader, property)} property" : "  property";
            members.Add($"{prefix} {propertyName}");
        }
    }

    foreach (MethodDefinitionHandle methodHandle in type.GetMethods())
    {
        MethodDefinition method = reader.GetMethodDefinition(methodHandle);
        string methodName = reader.GetString(method.Name);
        if (typeMatches || regex.IsMatch(methodName))
        {
            if (includeSignatures)
            {
                MethodSignature<string> signature = method.DecodeSignature(signatureProvider, null);
                string prefix = includeAccessibility ? $"  {MethodAccessibility(method.Attributes)} method" : "  method";
                members.Add(
                    $"{prefix} {signature.ReturnType} {methodName}({string.Join(", ", signature.ParameterTypes)})"
                );
            }
            else
            {
                string prefix = includeAccessibility ? $"  {MethodAccessibility(method.Attributes)} method" : "  method";
                members.Add($"{prefix} {methodName}");
            }
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

static string FieldAccessibility(FieldAttributes attributes)
{
    return (attributes & FieldAttributes.FieldAccessMask) switch
    {
        FieldAttributes.Public => "public",
        FieldAttributes.Private => "private",
        FieldAttributes.Family => "protected",
        FieldAttributes.Assembly => "internal",
        FieldAttributes.FamORAssem => "protected_internal",
        FieldAttributes.FamANDAssem => "private_protected",
        _ => "unknown"
    };
}

static string MethodAccessibility(MethodAttributes attributes)
{
    return (attributes & MethodAttributes.MemberAccessMask) switch
    {
        MethodAttributes.Public => "public",
        MethodAttributes.Private => "private",
        MethodAttributes.Family => "protected",
        MethodAttributes.Assembly => "internal",
        MethodAttributes.FamORAssem => "protected_internal",
        MethodAttributes.FamANDAssem => "private_protected",
        _ => "unknown"
    };
}

static string PropertyAccessibility(MetadataReader reader, PropertyDefinition property)
{
    PropertyAccessors accessors = property.GetAccessors();
    List<string> accessorAccess = [];
    if (!accessors.Getter.IsNil)
    {
        accessorAccess.Add($"get:{MethodAccessibility(reader.GetMethodDefinition(accessors.Getter).Attributes)}");
    }
    if (!accessors.Setter.IsNil)
    {
        accessorAccess.Add($"set:{MethodAccessibility(reader.GetMethodDefinition(accessors.Setter).Attributes)}");
    }

    return accessorAccess.Count == 0 ? "unknown" : string.Join(",", accessorAccess);
}

static string TypeName(MetadataReader reader, TypeDefinition type)
{
    string ns = reader.GetString(type.Namespace);
    string name = reader.GetString(type.Name);
    return string.IsNullOrEmpty(ns) ? name : $"{ns}.{name}";
}

sealed class SignatureTextProvider : ISignatureTypeProvider<string, object?>
{
    public string GetArrayType(string elementType, ArrayShape shape)
    {
        return $"{elementType}[{new string(',', shape.Rank - 1)}]";
    }

    public string GetByReferenceType(string elementType)
    {
        return $"{elementType}&";
    }

    public string GetFunctionPointerType(MethodSignature<string> signature)
    {
        return $"fnptr({string.Join(", ", signature.ParameterTypes)})";
    }

    public string GetGenericInstantiation(string genericType, ImmutableArray<string> typeArguments)
    {
        return $"{genericType}<{string.Join(", ", typeArguments)}>";
    }

    public string GetGenericMethodParameter(object? genericContext, int index)
    {
        return $"!!{index}";
    }

    public string GetGenericTypeParameter(object? genericContext, int index)
    {
        return $"!{index}";
    }

    public string GetModifiedType(string modifier, string unmodifiedType, bool isRequired)
    {
        return unmodifiedType;
    }

    public string GetPinnedType(string elementType)
    {
        return elementType;
    }

    public string GetPointerType(string elementType)
    {
        return $"{elementType}*";
    }

    public string GetPrimitiveType(PrimitiveTypeCode typeCode)
    {
        return typeCode.ToString();
    }

    public string GetSZArrayType(string elementType)
    {
        return $"{elementType}[]";
    }

    public string GetTypeFromDefinition(MetadataReader reader, TypeDefinitionHandle handle, byte rawTypeKind)
    {
        TypeDefinition type = reader.GetTypeDefinition(handle);
        return TypeName(reader.GetString(type.Namespace), reader.GetString(type.Name));
    }

    public string GetTypeFromReference(MetadataReader reader, TypeReferenceHandle handle, byte rawTypeKind)
    {
        TypeReference type = reader.GetTypeReference(handle);
        return TypeName(reader.GetString(type.Namespace), reader.GetString(type.Name));
    }

    public string GetTypeFromSpecification(
        MetadataReader reader,
        object? genericContext,
        TypeSpecificationHandle handle,
        byte rawTypeKind
    )
    {
        return reader.GetTypeSpecification(handle).DecodeSignature(this, genericContext);
    }

    private static string TypeName(string ns, string name)
    {
        return string.IsNullOrEmpty(ns) ? name : $"{ns}.{name}";
    }
}
