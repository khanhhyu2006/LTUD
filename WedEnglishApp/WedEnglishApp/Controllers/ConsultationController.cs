using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using WedEnglishApp.Data;
using WedEnglishApp.Models;
using WedEnglishApp.Services;
using WedEnglishApp.ViewModels.Consultations;
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
        var guestIds=Request.Cookies.Keys.Where(k=>k.StartsWith("HITC.Consultation.")).Select(k=>int.TryParse(k["HITC.Consultation.".Length..],out var id)?id:0).Where(id=>id>0).Take(30).ToArray();
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
        if (!await ConsultationMessaging.AddAsync(context,conversation,body!,false,conversation.OwnerAccountId)) return BadRequest(new{error="Cuộc tư vấn đã kết thúc hoặc không còn khả dụng."});
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
