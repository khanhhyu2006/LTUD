using System.Text;
namespace WedEnglishApp.Services;
public static class CsvExport
{
    public static byte[] Bytes(IEnumerable<IEnumerable<string>> rows)
    {
        static string Cell(string value)
        {
            value ??= "";
            if (value.TrimStart().Length > 0 && "=+-@".Contains(value.TrimStart()[0]) || value.StartsWith('\t') || value.StartsWith('\r')) value = "'" + value;
            return "\"" + value.Replace("\"", "\"\"") + "\"";
        }
        var text = string.Join("\r\n", rows.Select(row => string.Join(",", row.Select(Cell))));
        return Encoding.UTF8.GetPreamble().Concat(Encoding.UTF8.GetBytes(text)).ToArray();
    }
}
