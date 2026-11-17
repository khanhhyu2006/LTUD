using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;

namespace WedEnglishApp.Services
{
    public static class ImageUploadStorage
    {
        public static async Task<string> SaveAsync(IWebHostEnvironment environment, IFormFile file, string folderName)
        {
            var webRootPath = environment.WebRootPath ?? Path.Combine(environment.ContentRootPath, "wwwroot");
            var uploadFolder = Path.Combine(webRootPath, "uploads", folderName);
            Directory.CreateDirectory(uploadFolder);

            var extension = Path.GetExtension(file.FileName).ToLowerInvariant();
            var fileName = $"{Guid.NewGuid():N}{extension}";
            var filePath = Path.Combine(uploadFolder, fileName);

            await using var stream = new FileStream(filePath, FileMode.CreateNew);
            await file.CopyToAsync(stream);

            return $"/uploads/{folderName}/{fileName}";
        }
    }
}
