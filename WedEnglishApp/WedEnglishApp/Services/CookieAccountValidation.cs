using System.Security.Claims;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
namespace WedEnglishApp.Services;
public static class CookieAccountValidation
{
    public static async Task ValidateAsync(CookieValidatePrincipalContext context)
    {
        int.TryParse(context.Principal?.FindFirstValue(ClaimTypes.NameIdentifier), out var id);
        var role = context.Principal?.FindFirstValue(ClaimTypes.Role);
        var db = context.HttpContext.RequestServices.GetRequiredService<ApplicationDbContext>();
        if (!await db.UserAccounts.AnyAsync(a => a.AccountId == id && a.IsActive && !a.IsDeleted && a.Role == role))
        {
            context.RejectPrincipal();
            await context.HttpContext.SignOutAsync(context.Scheme.Name);
        }
    }
}
