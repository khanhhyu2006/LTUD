from pathlib import Path
p=Path('WedEnglishApp/Services/ConsultationMessaging.cs');s=p.read_text(encoding='utf8').replace('public static async Task AddAsync','public static async Task<bool> AddAsync');a=s.index('        context.ConsultationMessages.Add');b=s.index('    public static async Task<object> FeedAsync',a);s=s[:a]+'''        await using var transaction = await context.Database.BeginTransactionAsync();
        var updated = await context.Consultations.Where(c => c.ConsultationId == conversation.ConsultationId && !c.IsDeleted && c.Status != "Closed")
            .ExecuteUpdateAsync(update => update.SetProperty(c => c.Status, isAdmin ? "Replied" : "Pending").SetProperty(c => c.LastMessageAt, DateTime.Now));
        if (updated == 0) return false;
        context.ConsultationMessages.Add(new ConsultationMessage
        {
            ConsultationId = conversation.ConsultationId, Body = body.Trim(),
            SenderRole = isAdmin ? "Admin" : "Customer", SenderAccountId = accountId, SentAt = DateTime.Now
        });
        await context.SaveChangesAsync();
        await transaction.CommitAsync();
        return true;
    }
'''+s[b:];p.write_text(s,encoding='utf8')
for f in ['WedEnglishApp/Controllers/ConsultationController.cs','WedEnglishApp/Areas/Admin/Controllers/ConsultationManagerController.cs']:
 p=Path(f);s=p.read_text(encoding='utf8');s=s.replace('await ConsultationMessaging.AddAsync(context,conversation,body!,false,conversation.OwnerAccountId);','if (!await ConsultationMessaging.AddAsync(context,conversation,body!,false,conversation.OwnerAccountId)) return BadRequest(new{error="Cuộc tư vấn đã kết thúc hoặc không còn khả dụng."});');s=s.replace('await ConsultationMessaging.AddAsync(context,conversation,body!,true,accountId);','if (!await ConsultationMessaging.AddAsync(context,conversation,body!,true,accountId)) return BadRequest(new{error="Cuộc tư vấn đã kết thúc hoặc không còn khả dụng."});');p.write_text(s,encoding='utf8')
p=Path('WedEnglishApp/Views/Home/Contact.cshtml');s=p.read_text(encoding='utf8');s=s.replace('<label class="form-label fw-semibold">Họ và tên','<label for="contact-name" class="form-label fw-semibold">Họ và tên').replace('<label class="form-label fw-semibold">Email','<label for="contact-email" class="form-label fw-semibold">Email').replace('<label class="form-label fw-semibold">Số điện thoại','<label for="contact-phone" class="form-label fw-semibold">Số điện thoại').replace('<label class="form-label fw-semibold">Nội dung','<label for="contact-question" class="form-label fw-semibold">Nội dung');p.write_text(s,encoding='utf8')
