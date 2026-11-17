using Microsoft.AspNetCore.Http;

namespace WedEnglishApp.Services
{
    public static class ImageUploadValidator
    {
        public const long MaxFileSizeBytes = 5 * 1024 * 1024;

        public static async Task<string?> GetValidatedExtensionAsync(IFormFile file)
        {
            if (file.Length == 0 || file.Length > MaxFileSizeBytes)
            {
                return null;
            }

            var extension = Path.GetExtension(file.FileName).ToLowerInvariant();
            var header = new byte[12];
            await using var stream = file.OpenReadStream();
            var bytesRead = await stream.ReadAsync(header.AsMemory());

            var isValidImage = extension switch
            {
                ".jpg" or ".jpeg" => bytesRead >= 3 && header[0] == 0xFF && header[1] == 0xD8 && header[2] == 0xFF,
                ".png" => bytesRead >= 8 && header[0] == 0x89 && header[1] == 0x50 && header[2] == 0x4E && header[3] == 0x47 && header[4] == 0x0D && header[5] == 0x0A && header[6] == 0x1A && header[7] == 0x0A,
                ".webp" => bytesRead >= 12 && header[0] == 0x52 && header[1] == 0x49 && header[2] == 0x46 && header[3] == 0x46 && header[8] == 0x57 && header[9] == 0x45 && header[10] == 0x42 && header[11] == 0x50,
                _ => false
            };

            return isValidImage ? extension : null;
        }
    }
}
