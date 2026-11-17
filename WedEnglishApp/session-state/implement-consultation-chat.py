from pathlib import Path
base=Path('WedEnglishApp')
def r(f):return(base/f).read_text(encoding='utf8')
def w(f,s):
 p=base/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
w('Services/ConsultationMessaging.cs','''using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
namespace WedEnglishApp.Services;

public static class ConsultationMessaging
{
    public static string? Validate(Consultation conversation, string? body)
    {
        if (conversation.Status == "Closed") return "Cuộc tư vấn đã kết thúc. Vui lòng tạo yêu cầu mới hoặc chờ Admin mở lại.";
        if (string.IsNullOrWhiteSpace(body) || body.Trim().Length > 2000) return "Tin nhắn cần từ 1 đến 2000 ký tự.";
        return null;
    }
    public static async Task AddAsync(ApplicationDbContext context, Consultation conversation, string body, bool isAdmin, int? accountId)
    {
        context.ConsultationMessages.Add(new ConsultationMessage
        {
            ConsultationId = conversation.ConsultationId, Body = body.Trim(),
            SenderRole = isAdmin ? "Admin" : "Customer", SenderAccountId = accountId, SentAt = DateTime.Now
        });
        conversation.Status = isAdmin ? "Replied" : "Pending";
        context.Entry(conversation).Property(c => c.Status).IsModified = true;
        conversation.LastMessageAt = DateTime.Now;
        await context.SaveChangesAsync();
    }
    public static async Task<object> FeedAsync(ApplicationDbContext context, Consultation conversation, int afterId)
    {
        var messages = await context.ConsultationMessages.Where(m => m.ConsultationId == conversation.ConsultationId && m.MessageId > afterId)
            .OrderBy(m => m.MessageId).Take(100).Select(m => new { id=m.MessageId, body=m.Body, isAdmin=m.SenderRole=="Admin", sentAt=m.SentAt }).ToListAsync();
        return new { status=conversation.Status, messages };
    }
    public static async Task MarkReadAsync(ApplicationDbContext context, Consultation conversation, int lastMessageId, bool isAdmin)
    {
        var bounded = await context.ConsultationMessages.Where(m => m.ConsultationId == conversation.ConsultationId && m.MessageId <= lastMessageId).MaxAsync(m => (int?)m.MessageId) ?? 0;
        if (isAdmin)
            await context.Consultations.Where(c => c.ConsultationId == conversation.ConsultationId && c.AdminLastReadMessageId < bounded).ExecuteUpdateAsync(s => s.SetProperty(c => c.AdminLastReadMessageId, bounded));
        else
            await context.Consultations.Where(c => c.ConsultationId == conversation.ConsultationId && c.CustomerLastReadMessageId < bounded).ExecuteUpdateAsync(s => s.SetProperty(c => c.CustomerLastReadMessageId, bounded));
    }
}
''')
w('Controllers/ConsultationController.cs','''using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
using WedEnglishApp.Services;
using WedEnglishApp.ViewModels.Consultation;
namespace WedEnglishApp.Controllers;

[ResponseCache(NoStore=true,Location=ResponseCacheLocation.None)]
public class ConsultationController(ApplicationDbContext context, ConsultationAccess access) : Controller
{
    [HttpPost, ValidateAntiForgeryToken]
    public async Task<IActionResult> Submit(StartConsultationViewModel model)
    {
        var student = await access.StudentAsync(HttpContext);
        model.IsStudent = student != null;
        if (student != null)
        {
            model.ContactName = student.FullName; model.ContactEmail = student.Email;
            if (string.IsNullOrWhiteSpace(model.PhoneNumber)) model.PhoneNumber = student.Student?.PhoneNumber ?? "";
        }
        ModelState.Clear();
        if (!TryValidateModel(model)) return View("~/Views/Home/Contact.cshtml",model);
        var token = student == null ? ConsultationAccess.Token() : null;
        var conversation = new Consultation
        {
            ContactName=model.ContactName.Trim(),ContactEmail=model.ContactEmail.Trim().ToLowerInvariant(),
            PhoneNumber=model.PhoneNumber.Trim(),Question=model.Question.Trim(),OwnerAccountId=student?.AccountId,
            GuestAccessHash=token==null ? null : ConsultationAccess.Hash(token),Status="Pending",LastMessageAt=DateTime.Now
        };
        conversation.Messages.Add(new ConsultationMessage { Body=conversation.Question,SenderRole="Customer",SenderAccountId=student?.AccountId });
        context.Consultations.Add(conversation); await context.SaveChangesAsync();
        if (token != null) ConsultationAccess.Remember(HttpContext,conversation.ConsultationId,token);
        return RedirectToAction(nameof(Thread),new{id=conversation.ConsultationId});
    }
    private async Task<Consultation?> OwnedAsync(int id, bool withMessages=false)
    {
        var query = context.Consultations.AsQueryable();
        if (withMessages) query=query.Include(c=>c.Messages);
        var conversation = await query.FirstOrDefaultAsync(c=>c.ConsultationId==id && !c.IsDeleted);
        return conversation != null && await access.CanReadAsync(HttpContext,conversation) ? conversation : null;
    }
    public async Task<IActionResult> Thread(int id)
    {
        var conversation=await OwnedAsync(id,true); if(conversation==null)return NotFound();
        Response.Headers["Referrer-Policy"]="no-referrer";
        var token=conversation.OwnerAccountId==null ? Request.Cookies[ConsultationAccess.CookieName(id)] : null;
        return View(new ConsultationThreadViewModel
        {
            Conversation=conversation, FeedUrl=Url.Action(nameof(Messages),new{id})!,SendUrl=Url.Action(nameof(Send),new{id})!,ReadUrl=Url.Action(nameof(Read),new{id})!,
            RecoveryUrl=token==null ? null : Url.Action(nameof(Open),"Consultation",new{id,token},Request.Scheme)
        });
    }
    public async Task<IActionResult> Mine()
    {
        var student=await access.StudentAsync(HttpContext);
        var owned=student==null ? new List<Consultation>() : await context.Consultations.Include(c=>c.Messages).Where(c=>c.OwnerAccountId==student.AccountId&&!c.IsDeleted).OrderByDescending(c=>c.LastMessageAt).ToListAsync();
        var guestIds=Request.Cookies.Keys.Where(k=>k.StartsWith("HITC.Consultation.")).Select(k=>int.TryParse(k[18..],out var id)?id:0).Where(id=>id>0).Take(30).ToArray();
        var guests=await context.Consultations.Include(c=>c.Messages).Where(c=>c.OwnerAccountId==null&&!c.IsDeleted&&guestIds.Contains(c.ConsultationId)).ToListAsync();
        owned.AddRange(guests.Where(c=>ConsultationAccess.Matches(c.GuestAccessHash,Request.Cookies[ConsultationAccess.CookieName(c.ConsultationId)])));
        return View(owned.OrderByDescending(c=>c.LastMessageAt).ToList());
    }
    public async Task<IActionResult> Open(int id,string? token)
    {
        Response.Headers["Referrer-Policy"]="no-referrer";
        var conversation=await context.Consultations.FirstOrDefaultAsync(c=>c.ConsultationId==id&&!c.IsDeleted&&c.OwnerAccountId==null);
        if(conversation==null||!ConsultationAccess.Matches(conversation.GuestAccessHash,token))return NotFound();
        ConsultationAccess.Remember(HttpContext,id,token!);
        return RedirectToAction(nameof(Thread),new{id});
    }
    public async Task<IActionResult> Messages(int id,int afterId=0)
    {
        var conversation=await OwnedAsync(id);if(conversation==null)return NotFound();
        return Json(await ConsultationMessaging.FeedAsync(context,conversation,Math.Max(0,afterId)));
    }
    [HttpPost,ValidateAntiForgeryToken]
    public async Task<IActionResult> Send(int id,string? body)
    {
        var conversation=await OwnedAsync(id);if(conversation==null)return NotFound();
        var error=ConsultationMessaging.Validate(conversation,body);
        if(error!=null)return BadRequest(new{error});
        await ConsultationMessaging.AddAsync(context,conversation,body!,false,conversation.OwnerAccountId);
        if(Request.Headers.Accept.ToString().Contains("application/json"))return Json(new{ok=true});
        return RedirectToAction(nameof(Thread),new{id});
    }
    [HttpPost,ValidateAntiForgeryToken]
    public async Task<IActionResult> Read(int id,int lastMessageId)
    {
        var conversation=await OwnedAsync(id);if(conversation==null)return NotFound();
        await ConsultationMessaging.MarkReadAsync(context,conversation,lastMessageId,false);return Ok();
    }
}
''')
# Prefix length is derived rather than copied into ownership parsing.
s=r('Controllers/ConsultationController.cs').replace('k[18..]','k["HITC.Consultation.".Length..]');w('Controllers/ConsultationController.cs',s)
w('Areas/Admin/Controllers/ConsultationManagerController.cs','''using System.Security.Claims;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Services;
using WedEnglishApp.ViewModels.Consultation;
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
        await ConsultationMessaging.AddAsync(context,conversation,body!,true,accountId);
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
''')
s=r('Controllers/HomeController.cs');s=s.replace('private readonly ApplicationDbContext _context;','private readonly ApplicationDbContext _context;\n        private readonly WedEnglishApp.Services.ConsultationAccess _consultationAccess;').replace('public HomeController(ApplicationDbContext context)','public HomeController(ApplicationDbContext context, WedEnglishApp.Services.ConsultationAccess consultationAccess)').replace('_context = context;','_context = context;\n            _consultationAccess = consultationAccess;');s=s.replace('''        public IActionResult Contact()
        {
            return View();
        }''','''        public async Task<IActionResult> Contact()
        {
            var student = await _consultationAccess.StudentAsync(HttpContext);
            return View(new WedEnglishApp.ViewModels.Consultation.StartConsultationViewModel
            {
                IsStudent=student!=null, ContactName=student?.FullName??"", ContactEmail=student?.Email??"", PhoneNumber=student?.Student?.PhoneNumber??""
            });
        }''');w('Controllers/HomeController.cs',s)
print('Guest/student ownership, live messaging endpoints and admin inbox implemented')
