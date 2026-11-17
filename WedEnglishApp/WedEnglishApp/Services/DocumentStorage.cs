using System.IO.Compression;
namespace WedEnglishApp.Services;
public class DocumentStorage(IWebHostEnvironment env)
{
    public const long MaxBytes = 10 * 1024 * 1024;
    private static readonly HashSet<string> Extensions = new(StringComparer.OrdinalIgnoreCase) { ".pdf", ".docx", ".pptx", ".xlsx", ".txt" };
    public async Task<string?> ValidateAsync(IFormFile? file)
    {
        if (file == null || file.Length == 0 || file.Length > MaxBytes) return "Tệp phải có nội dung và không quá 10 MB.";
        var ext = Path.GetExtension(file.FileName).ToLowerInvariant();
        if (!Extensions.Contains(ext)) return "Chỉ nhận PDF, DOCX, PPTX, XLSX hoặc TXT.";
        try
        {
            await using var input = file.OpenReadStream();
            var header = new byte[5]; var read = await input.ReadAsync(header);
            if (ext == ".pdf" && (read < 5 || !header.AsSpan().SequenceEqual("%PDF-"u8))) return "Nội dung tệp PDF không hợp lệ.";
            if (ext == ".txt")
            {
                input.Position = 0;
                using var reader = new StreamReader(input, new System.Text.UTF8Encoding(false, true), true);
                var text = await reader.ReadToEndAsync();
                if (text.Contains('\0')) return "Tệp TXT phải là văn bản hợp lệ.";
            }
            if (ext is ".docx" or ".pptx" or ".xlsx")
            {
                if (file.Length < 22) return "Cấu trúc tệp Office không hợp lệ.";
                input.Position = 0;
                using var zip = new ZipArchive(input, ZipArchiveMode.Read);
                var entry = ext == ".docx" ? "word/document.xml" : ext == ".pptx" ? "ppt/presentation.xml" : "xl/workbook.xml";
                if (zip.GetEntry("[Content_Types].xml") == null || zip.GetEntry(entry) == null
                    || zip.Entries.Count > 2048 || zip.Entries.Sum(e => e.Length) > 100L * 1024 * 1024)
                    return "Cấu trúc tệp Office không hợp lệ hoặc quá lớn.";
            }
        }
        catch (Exception ex) when (ex is InvalidDataException or IOException or ArgumentException or System.Text.DecoderFallbackException)
        { return "Không thể đọc nội dung tệp. Vui lòng chọn tệp hợp lệ."; }
        return null;
    }
    public async Task<string> SaveAsync(IFormFile file)
    {
        var directory = Path.Combine(env.ContentRootPath, "App_Data", "ClassDocuments");
        Directory.CreateDirectory(directory);
        var name = Guid.NewGuid().ToString("N") + Path.GetExtension(file.FileName).ToLowerInvariant();
        await using var target = new FileStream(Path.Combine(directory, name), FileMode.CreateNew);
        await file.CopyToAsync(target);
        return "private-documents/" + name;
    }
    public string? Resolve(string value)
    {
        if (string.IsNullOrWhiteSpace(value)) return null;
        var prefix = value.StartsWith("private-documents/", StringComparison.Ordinal) ? "private-documents/" : "/uploads/documents/";
        if (!value.StartsWith(prefix, StringComparison.Ordinal)) return null;
        var name = value[prefix.Length..];
        if (string.IsNullOrWhiteSpace(name) || name != Path.GetFileName(name) || name.Contains('\\') || name.Contains('/') || name.Contains(':')) return null;
        var directory = prefix == "private-documents/" ? Path.Combine(env.ContentRootPath, "App_Data", "ClassDocuments") : Path.Combine(env.WebRootPath, "uploads", "documents");
        var full = Path.GetFullPath(Path.Combine(directory, name));
        return full.StartsWith(Path.GetFullPath(directory) + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase) && File.Exists(full) ? full : null;
    }
    public void TryDelete(string value)
    {
        // Only private, generated filenames may be removed; legacy files are retained for recovery.
        if (!value.StartsWith("private-documents/", StringComparison.Ordinal)) return;
        var file = Resolve(value);
        if (file != null) { try { File.Delete(file); } catch (IOException) { } catch (UnauthorizedAccessException) { } }
    }
}
