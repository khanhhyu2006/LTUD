using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Services;
using WedEnglishApp.ViewModels.Consultations;
namespace WedEnglishApp.Areas.Admin.Controllers;

[Area("Admin"),Authorize(Roles="Admin"),ResponseCache(NoStore=true,Location=ResponseCacheLocation.None)]
public class ConsultationManagerController(ApplicationDbContext context) : Controller
{
    public async Task<IActionResult> Index()
    {
        return View(await context.Consultations.Include(c=>c.Messages).Where(c=>!c.IsDeleted).OrderByDescending(c=>c.LastMessageAt).ToListAsync());
    }
    public async Task<IActionResult> Details(int id)
    {
        var conversation=await context.Consultations.Include(c=>c.Messages).FirstOrDefaultAsync(c=>c.ConsultationId==id&&!c.IsDeleted);
        if(conversation==null)return NotFound();
        return View(new ConsultationThreadViewModel { Conversation=conversation,IsAdmin=true,FeedUrl=Url.Action(nameof(Messages),new{id})!,SendUrl=Url.Action(nameof(Reply),new{id})!,ReadUrl=Url.Action(nameof(Read),new{id})! });
    }
    public async Task<IActionResult> Messages(int id,int afterId=0)
    {
        var conversation=await context.Consultations.FirstOrDefaultAsync(c=>c.ConsultationId==id&&!c.IsDeleted);if(conversation==null)return NotFound();
        return Json(await ConsultationMessaging.FeedAsync(context,conversation,Math.Max(0,afterId)));
    }
    [HttpPost,ValidateAntiForgeryToken]
    public async Task<IActionResult> Reply(int id,string? body)
    {
        var conversation=await context.Consultations.FirstOrDefaultAsync(c=>c.ConsultationId==id&&!c.IsDeleted);if(conversation==null)return NotFound();
        var error=ConsultationMessaging.Validate(conversation,body);if(error!=null)return BadRequest(new{error});
        if(!int.TryParse(User.FindFirstValue(ClaimTypes.NameIdentifier),out var accountId))return Forbid();
        if (!await ConsultationMessaging.AddAsync(context,conversation,body!,true,accountId)) return BadRequest(new{error="Cuộc tư vấn đã kết thúc hoặc không còn khả dụng."});
        if(Request.Headers.Accept.ToString().Contains("application/json"))return Json(new{ok=true});
        return RedirectToAction(nameof(Details),new{id});
    }
    [HttpPost,ValidateAntiForgeryToken]
    public async Task<IActionResult> Read(int id,int lastMessageId)
    {
        var conversation=await context.Consultations.FirstOrDefaultAsync(c=>c.ConsultationId==id&&!c.IsDeleted);if(conversation==null)return NotFound();
        await ConsultationMessaging.MarkReadAsync(context,conversation,lastMessageId,true);return Ok();
    }
    public async Task<IActionResult> InboxUpdates()
    {
        var rows=await context.Consultations.Where(c=>!c.IsDeleted).OrderBy(c=>c.ConsultationId).Select(c=>new{c.ConsultationId,c.LastMessageAt,c.Status,c.AdminLastReadMessageId}).ToListAsync();
        return Json(new{signature=string.Join("|",rows.Select(c=>$"{c.ConsultationId}:{c.LastMessageAt.Ticks}:{c.Status}:{c.AdminLastReadMessageId}"))});
    }
    [HttpPost,ValidateAntiForgeryToken]
    public async Task<IActionResult> SetStatus(int id,bool closed)
    {
        var conversation=await context.Consultations.FirstOrDefaultAsync(c=>c.ConsultationId==id&&!c.IsDeleted);if(conversation==null)return NotFound();
        conversation.Status=closed?"Closed":"Pending";await context.SaveChangesAsync();
        return RedirectToAction(nameof(Details),new{id});
    }
    [HttpPost,ValidateAntiForgeryToken]
    public async Task<IActionResult> GuestLink(int id)
    {
        var conversation=await context.Consultations.FirstOrDefaultAsync(c=>c.ConsultationId==id&&!c.IsDeleted&&c.OwnerAccountId==null);
        if(conversation==null)return NotFound();
        if(conversation.GuestAccessHash!=null) { TempData["ErrorMessage"]="Khách đã có liên kết riêng; không thay đổi để tránh mất quyền theo dõi.";return RedirectToAction(nameof(Details),new{id}); }
        var token=ConsultationAccess.Token();conversation.GuestAccessHash=ConsultationAccess.Hash(token);await context.SaveChangesAsync();
        TempData["GuestLink"]=Url.Action("Open","Consultation",new{area="",id,token},Request.Scheme);
        return RedirectToAction(nameof(Details),new{id});
    }
    [HttpPost,ValidateAntiForgeryToken]
    public async Task<IActionResult> Delete(int id)
    {
        var conversation=await context.Consultations.FindAsync(id);if(conversation==null)return NotFound();
        conversation.IsDeleted=true;conversation.DeletedAt=DateTime.Now;await context.SaveChangesAsync();return RedirectToAction(nameof(Index));
    }
}
