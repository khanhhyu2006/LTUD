using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.WebUtilities;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
namespace WedEnglishApp.Services;

public class ConsultationAccess(ApplicationDbContext context)
{
    public async Task<UserAccount?> StudentAsync(HttpContext http)
    {
        var auth = await http.AuthenticateAsync("StudentCookie");
        if (!auth.Succeeded || !int.TryParse(auth.Principal?.FindFirstValue(ClaimTypes.NameIdentifier), out var id)) return null;
        return await context.UserAccounts.Include(u => u.Student).FirstOrDefaultAsync(u => u.AccountId == id && u.Role == "Student" && u.IsActive && !u.IsDeleted);
    }
    public static string CookieName(int id) => $"HITC.Consultation.{id}";
    public static string Token() => WebEncoders.Base64UrlEncode(RandomNumberGenerator.GetBytes(32));
    public static string Hash(string token) => Convert.ToHexString(SHA256.HashData(Encoding.UTF8.GetBytes(token)));
    public static bool Matches(string? hash, string? token)
    {
        if (hash?.Length != 64 || string.IsNullOrEmpty(token) || token.Length > 200) return false;
        try { return CryptographicOperations.FixedTimeEquals(Convert.FromHexString(hash), SHA256.HashData(Encoding.UTF8.GetBytes(token))); }
        catch (FormatException) { return false; }
    }
    public static void Remember(HttpContext http, int id, string token) => http.Response.Cookies.Append(CookieName(id), token,
        new CookieOptions { HttpOnly=true, Secure=http.Request.IsHttps, SameSite=SameSiteMode.Lax, Path="/Consultation", Expires=DateTimeOffset.UtcNow.AddDays(30), IsEssential=true });
    public async Task<bool> CanReadAsync(HttpContext http, Consultation conversation)
    {
        if (conversation.IsDeleted) return false;
        if (conversation.OwnerAccountId.HasValue) return (await StudentAsync(http))?.AccountId == conversation.OwnerAccountId.Value;
        return Matches(conversation.GuestAccessHash, http.Request.Cookies[CookieName(conversation.ConsultationId)]);
    }
}
