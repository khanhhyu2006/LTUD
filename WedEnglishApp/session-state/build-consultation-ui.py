from pathlib import Path
base=Path('WedEnglishApp')
def r(f):return(base/f).read_text(encoding='utf8')
def w(f,s):
 p=base/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf8')
w('Views/Shared/_ConsultationConversation.cshtml','''@model WedEnglishApp.ViewModels.Consultation.ConsultationThreadViewModel
@{ var ordered=Model.Conversation.Messages.OrderBy(m=>m.MessageId).ToList(); var lastId=ordered.LastOrDefault()?.MessageId??0; }
<div class="consultation-chat" data-feed-url="@Model.FeedUrl" data-send-url="@Model.SendUrl" data-read-url="@Model.ReadUrl" data-last-id="@lastId" data-admin="@Model.IsAdmin.ToString().ToLowerInvariant()" data-contact="@Model.Conversation.ContactName">
    <div class="d-flex flex-wrap justify-content-between gap-2 align-items-center mb-3">
        <h5 class="mb-0">Nội dung trao đổi</h5><span data-chat-status class="small text-muted">Tự cập nhật khi có tin nhắn mới</span>
    </div>
    <div class="consultation-log" role="log" aria-live="polite" aria-label="Lịch sử trao đổi tư vấn">
        @foreach(var message in ordered) {
            var own=(message.SenderRole=="Admin")==Model.IsAdmin;
            <div class="chat-message @(own?"chat-own":"chat-other")" data-message-id="@message.MessageId">
                <div class="small fw-semibold mb-1">@(own?"Bạn":message.SenderRole=="Admin"?"Tư vấn viên":Model.Conversation.ContactName)</div>
                <div class="chat-body">@message.Body</div>
                <div class="chat-time">@message.SentAt.ToString("HH:mm dd/MM/yyyy")</div>
            </div>
        }
    </div>
    <form action="@Model.SendUrl" method="post" class="chat-form mt-3">
        @Html.AntiForgeryToken()
        <label for="consultation-body" class="form-label">Tin nhắn của bạn</label>
        <textarea id="consultation-body" name="body" rows="3" maxlength="2000" class="form-control mb-2" placeholder="Nhập nội dung cần trao đổi..." required data-chat-control disabled="@(Model.Conversation.Status=="Closed")"></textarea>
        <div class="d-flex justify-content-between gap-2 align-items-center">
            <span class="small text-muted" data-chat-feedback role="status">@(Model.Conversation.Status=="Closed"?"Cuộc tư vấn đã kết thúc.":"Tối đa 2000 ký tự mỗi tin nhắn.")</span>
            <button type="submit" class="btn btn-primary px-4" data-chat-control disabled="@(Model.Conversation.Status=="Closed")">Gửi tin nhắn</button>
        </div>
    </form>
</div>
''')
w('wwwroot/css/consultation-chat.css','''.consultation-log{height:52vh;min-height:280px;max-height:560px;overflow-y:auto;padding:1rem;background:#f1f5f9;border-radius:.75rem;display:flex;flex-direction:column;gap:.85rem;border:1px solid #e2e8f0}
.chat-message{padding:.85rem 1rem;border-radius:.85rem;max-width:85%;width:fit-content;overflow-wrap:anywhere}
.chat-own{align-self:flex-end;background:#0757c7;color:#fff}
.chat-other{align-self:flex-start;background:#fff;color:#1e293b;border:1px solid #dbe3ec}
.chat-body{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.6}
.chat-time{font-size:.72rem;margin-top:.5rem;opacity:.85}
.consultation-chat .chat-form textarea{resize:vertical}
.consultation-inbox .message-preview{white-space:pre-wrap;overflow-wrap:anywhere;max-height:4.8em;overflow:hidden}
@media(max-width:575.98px){.chat-message{max-width:95%}.consultation-log{padding:.65rem}.chat-form .d-flex{flex-wrap:wrap}.chat-form button{width:100%}}
''')
w('wwwroot/js/consultation-chat.js','''(() => {
    const root=document.querySelector('.consultation-chat');
    document.querySelectorAll('[data-copy-link]').forEach(button=>button.addEventListener('click',async()=>{
        const input=document.getElementById(button.dataset.copyLink);
        try { await navigator.clipboard.writeText(input.value); button.textContent='Đã sao chép'; }
        catch { input.focus();input.select();button.textContent='Đã chọn liên kết để sao chép'; }
    }));
    if(!root)return;
    const log=root.querySelector('.consultation-log'),form=root.querySelector('.chat-form'),feedback=root.querySelector('[data-chat-feedback]'),connection=root.querySelector('[data-chat-status]');
    const token=form.querySelector('[name=__RequestVerificationToken]').value;
    const ownAdmin=root.dataset.admin==='true';
    let lastId=Number(root.dataset.lastId)||0,busy=false,sending=false,closed=form.querySelector('textarea').disabled;
    const seen=new Set([...log.querySelectorAll('[data-message-id]')].map(e=>Number(e.dataset.messageId)));
    const controls=[...form.querySelectorAll('[data-chat-control]')];
    function append(message){
        if(seen.has(message.id))return;
        seen.add(message.id);
        const own=message.isAdmin===ownAdmin,entry=document.createElement('div');
        entry.className='chat-message '+(own?'chat-own':'chat-other');entry.dataset.messageId=message.id;
        const author=document.createElement('div');author.className='small fw-semibold mb-1';author.textContent=own?'Bạn':message.isAdmin?'Tư vấn viên':root.dataset.contact;
        const body=document.createElement('div');body.className='chat-body';body.textContent=message.body;
        const time=document.createElement('div');time.className='chat-time';time.textContent=new Date(message.sentAt).toLocaleString('vi-VN');
        entry.append(author,body,time);log.append(entry);
    }
    async function markRead(){
        if(!lastId)return;
        const data=new URLSearchParams({__RequestVerificationToken:token,lastMessageId:String(lastId)});
        await fetch(root.dataset.readUrl,{method:'POST',body:data,credentials:'same-origin'}).catch(()=>{});
    }
    async function load(force=false){
        if(busy||document.hidden&&!force)return;
        busy=true;
        const nearBottom=log.scrollHeight-log.scrollTop-log.clientHeight<100;
        try{
            const url=new URL(root.dataset.feedUrl,location.origin);url.searchParams.set('afterId',lastId);
            const response=await fetch(url,{cache:'no-store',credentials:'same-origin',headers:{Accept:'application/json'}});
            if(!response.ok)throw new Error(response.status===404?'Cuộc tư vấn không còn khả dụng. Vui lòng tải lại trang.':'Đang kết nối lại...');
            const data=await response.json();
            for(const message of data.messages){append(message);lastId=Math.max(lastId,message.id);}
            closed=data.status==='Closed';controls.forEach(e=>e.disabled=closed||sending);
            if(closed)feedback.textContent='Cuộc tư vấn đã kết thúc. Bạn có thể gửi yêu cầu mới từ trang liên hệ.';
            connection.textContent='Đang kết nối · Tin nhắn tự cập nhật';
            if(nearBottom||force)log.scrollTop=log.scrollHeight;
            if(data.messages.length)await markRead();
        }catch(error){connection.textContent=error.message||'Đang kết nối lại...';}
        finally{busy=false;}
    }
    form.addEventListener('submit',async event=>{
        event.preventDefault();if(sending||closed||!form.reportValidity())return;
        const body=form.querySelector('[name=body]').value.trim();if(!body)return;
        const data=new URLSearchParams({__RequestVerificationToken:token,body});
        sending=true;controls.forEach(e=>e.disabled=true);feedback.textContent='Đang gửi...';
        try{
            const response=await fetch(root.dataset.sendUrl,{method:'POST',body:data,credentials:'same-origin',headers:{Accept:'application/json'}});
            const result=await response.json().catch(()=>({}));
            if(!response.ok)throw new Error(result.error||'Không gửi được tin nhắn. Vui lòng thử lại.');
            form.querySelector('[name=body]').value='';feedback.textContent='Đã gửi tin nhắn.';await load(true);
        }catch(error){feedback.textContent=error.message;}
        finally{sending=false;controls.forEach(e=>e.disabled=closed);}
    });
    log.scrollTop=log.scrollHeight;markRead();load(true);
    setInterval(()=>load(),2000);
    document.addEventListener('visibilitychange',()=>{if(!document.hidden)load(true);});
})();
''')
w('Views/Consultation/Thread.cshtml','''@model WedEnglishApp.ViewModels.Consultation.ConsultationThreadViewModel
@{ ViewData["Title"]="Tư vấn trực tiếp"; }
@section Styles { <link rel="stylesheet" href="~/css/consultation-chat.css" asp-append-version="true" /> }
<div class="container py-4"><div class="row justify-content-center"><div class="col-lg-10">
    <div class="d-flex flex-wrap justify-content-between gap-2 mb-3"><div><h3>Tư vấn với trung tâm</h3><p class="small text-muted mb-0">Cuộc trao đổi #@Model.Conversation.ConsultationId · @Model.Conversation.ContactName</p></div><a asp-action="Mine" class="btn btn-outline-primary align-self-start">Các cuộc tư vấn của tôi</a></div>
    @if(Model.RecoveryUrl!=null) { <details class="mb-3"><summary class="small text-primary">Lưu liên kết để xem lại cuộc tư vấn</summary><p class="small text-muted mt-2">Liên kết riêng cho phép mở lại cuộc trao đổi trên thiết bị khác. Chỉ giữ cho bạn, không chia sẻ công khai.</p><div class="input-group"><input id="recovery-link" class="form-control" value="@Model.RecoveryUrl" readonly aria-label="Liên kết theo dõi riêng" /><button class="btn btn-outline-primary" type="button" data-copy-link="recovery-link">Sao chép</button></div></details> }
    <div class="card border-0 shadow-sm p-3 p-md-4">@await Html.PartialAsync("_ConsultationConversation",Model)</div>
</div></div></div>
@section Scripts { <script src="~/js/consultation-chat.js" asp-append-version="true"></script> }
''')
w('Views/Consultation/Mine.cshtml','''@model List<WedEnglishApp.Models.Consultation>
@{ ViewData["Title"]="Tư vấn của tôi"; }
<div class="container py-5"><div class="d-flex flex-wrap justify-content-between gap-2 mb-4"><h3>Các cuộc tư vấn của tôi</h3><a asp-controller="Home" asp-action="Contact" class="btn btn-primary">Gửi yêu cầu tư vấn mới</a></div>
@if(!Model.Any()) { <p>Chưa có cuộc tư vấn nào trên tài khoản hoặc trình duyệt này. Nếu đã lưu liên kết riêng, bạn có thể dùng liên kết đó để mở lại cuộc trao đổi.</p> }
<div class="row g-3">@foreach(var c in Model) { var unread=c.Messages.Count(m=>m.SenderRole=="Admin"&&m.MessageId>c.CustomerLastReadMessageId);<div class="col-lg-6"><div class="card p-4 h-100"><div class="d-flex justify-content-between gap-2"><strong>Tư vấn #@c.ConsultationId</strong>@if(unread>0){<span class="badge bg-danger">@unread tin mới</span>}</div><p class="mt-3">@c.Question</p><p class="small text-muted">@c.LastMessageAt.ToString("HH:mm dd/MM/yyyy") · @(c.Status=="Closed"?"Đã kết thúc":c.Status=="Replied"?"Trung tâm đã trả lời":"Chờ trung tâm phản hồi")</p><a asp-action="Thread" asp-route-id="@c.ConsultationId" class="btn btn-outline-primary mt-auto">Mở cuộc trao đổi</a></div></div> }</div></div>
''')
w('Areas/Admin/Views/ConsultationManager/Index.cshtml','''@model List<WedEnglishApp.Models.Consultation>
@{ ViewData["Title"]="Hộp thư tư vấn"; }
@section Styles { <link rel="stylesheet" href="~/css/consultation-chat.css" asp-append-version="true" /> }
<div class="d-flex flex-wrap justify-content-between gap-2 mb-4"><div><h3>Tư vấn trực tiếp với học viên và khách</h3><p class="text-muted mb-0">Mở cuộc trao đổi để trả lời. Danh sách tự cập nhật khi có tin nhắn mới.</p></div><span class="badge bg-primary align-self-start">@Model.Count(c=>c.Status=="Pending") cuộc chờ phản hồi</span></div>
<div class="admin-card consultation-inbox"><div class="table-responsive"><table class="table align-middle"><thead><tr><th>Người liên hệ</th><th>Tin nhắn gần nhất</th><th>Cập nhật</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>
@foreach(var c in Model) { var last=c.Messages.OrderByDescending(m=>m.MessageId).FirstOrDefault();var unread=c.Messages.Count(m=>m.SenderRole=="Customer"&&m.MessageId>c.AdminLastReadMessageId);<tr><td><strong>@c.ContactName</strong><div class="small">@(c.OwnerAccountId.HasValue?"Học viên":"Khách tư vấn")</div><div class="small">@c.ContactEmail</div><div class="small">@c.PhoneNumber</div></td><td><div class="message-preview">@(last?.Body??c.Question)</div>@if(unread>0){<span class="badge bg-danger mt-2">@unread tin chưa đọc</span>}</td><td class="small">@c.LastMessageAt.ToString("HH:mm dd/MM/yyyy")</td><td><span class="badge @(c.Status=="Closed"?"bg-secondary":c.Status=="Replied"?"bg-success":"bg-warning text-dark")">@(c.Status=="Closed"?"Đã kết thúc":c.Status=="Replied"?"Đã phản hồi":"Chờ phản hồi")</span></td><td><a asp-action="Details" asp-route-id="@c.ConsultationId" class="btn btn-primary btn-sm">Mở và trả lời</a></td></tr> }
@if(!Model.Any()){<tr><td colspan="5" class="text-muted text-center py-4">Chưa có cuộc tư vấn.</td></tr>}
</tbody></table></div></div>
@section Scripts { <script>
(()=>{let signature=null,busy=false;async function refresh(){if(busy||document.hidden)return;busy=true;try{const r=await fetch('@Url.Action("InboxUpdates")',{cache:'no-store'});if(!r.ok)return;const data=await r.json();if(signature!==null&&signature!==data.signature)location.reload();signature=data.signature;}catch{}finally{busy=false;}}refresh();setInterval(refresh,5000);})();
</script> }
''')
w('Areas/Admin/Views/ConsultationManager/Details.cshtml','''@model WedEnglishApp.ViewModels.Consultation.ConsultationThreadViewModel
@{ ViewData["Title"]="Trao đổi tư vấn"; }
@section Styles { <link rel="stylesheet" href="~/css/consultation-chat.css" asp-append-version="true" /> }
<div class="d-flex flex-wrap justify-content-between align-items-start gap-3 mb-3"><div><h3>Tư vấn #@Model.Conversation.ConsultationId · @Model.Conversation.ContactName</h3><p class="small mb-0">@(Model.Conversation.OwnerAccountId.HasValue?"Học viên":"Khách tư vấn") · @Model.Conversation.ContactEmail · @Model.Conversation.PhoneNumber</p></div><a asp-action="Index" class="btn btn-outline-secondary">Hộp thư tư vấn</a></div>
@if(TempData["GuestLink"] is string link) { <div class="mb-3"><p>Liên kết riêng đã được cấp. Bạn có thể cung cấp cho đúng khách để họ xem và trả lời:</p><div class="input-group"><input id="admin-guest-link" value="@link" readonly class="form-control" aria-label="Liên kết dành cho khách" /><button type="button" class="btn btn-outline-primary" data-copy-link="admin-guest-link">Sao chép</button></div></div> }
<div class="admin-card p-3 p-md-4 mb-3">@await Html.PartialAsync("_ConsultationConversation",Model)</div>
<div class="d-flex flex-wrap gap-2">
<form asp-action="SetStatus" method="post">@Html.AntiForgeryToken()<input type="hidden" name="id" value="@Model.Conversation.ConsultationId" /><input type="hidden" name="closed" value="@(Model.Conversation.Status!="Closed"?"true":"false")" /><button class="btn btn-outline-secondary">@(Model.Conversation.Status=="Closed"?"Mở lại cuộc tư vấn":"Kết thúc tư vấn")</button></form>
@if(Model.Conversation.OwnerAccountId==null&&Model.Conversation.GuestAccessHash==null) { <form asp-action="GuestLink" method="post">@Html.AntiForgeryToken()<input type="hidden" name="id" value="@Model.Conversation.ConsultationId" /><button class="btn btn-outline-primary">Cấp liên kết theo dõi cho khách cũ</button></form> }
<form asp-action="Delete" method="post" onsubmit="return confirm('Chuyển cuộc tư vấn này vào thùng rác?');">@Html.AntiForgeryToken()<input type="hidden" name="id" value="@Model.Conversation.ConsultationId" /><button class="btn btn-outline-danger">Chuyển vào thùng rác</button></form>
</div>
@section Scripts { <script src="~/js/consultation-chat.js" asp-append-version="true"></script> }
''')
# The contact page is the single entry point, with server-filled identity for students.
s=r('Views/Home/Contact.cshtml');s='@model WedEnglishApp.ViewModels.Consultation.StartConsultationViewModel\n'+s;s=s.replace('row g-5','row g-4 g-lg-5').replace('Gửi thắc mắc trực tuyến','Trao đổi trực tiếp với Admin');s=s.replace('                <form asp-controller="Consultation"', '''                <p class="small text-muted">Gửi lời nhắn đầu tiên để mở cuộc tư vấn. Bạn có thể xem phản hồi và nhắn tiếp ngay trên website.</p>
                <a asp-controller="Consultation" asp-action="Mine" class="btn btn-outline-primary mb-3">Xem các cuộc tư vấn của tôi</a>
                <form asp-controller="Consultation"''');s=s.replace('                    @Html.AntiForgeryToken()','                    @Html.AntiForgeryToken()\n                    <div asp-validation-summary="All" class="text-danger small"></div>');s=s.replace('<input type="text" name="ContactName" class="form-control" placeholder="Nguyễn Văn A" required />','<input asp-for="ContactName" id="contact-name" class="form-control" maxlength="100" readonly="@Model.IsStudent" required />');s=s.replace('<input type="email" name="ContactEmail" class="form-control" placeholder="example@gmail.com" required />','<input asp-for="ContactEmail" id="contact-email" type="email" class="form-control" maxlength="100" readonly="@Model.IsStudent" required />');s=s.replace('<input type="tel" name="PhoneNumber" class="form-control" placeholder="0901234567" required />','<input asp-for="PhoneNumber" id="contact-phone" type="tel" class="form-control" maxlength="20" placeholder="0901234567" required />');s=s.replace('<textarea name="Question" rows="4" class="form-control" placeholder="Nhập câu hỏi bạn cần giải đáp..." required></textarea>','<textarea asp-for="Question" id="contact-question" rows="4" maxlength="1000" class="form-control" placeholder="Bạn muốn được tư vấn về khóa học, lịch học hay học phí?" required></textarea>');s=s.replace('Gửi Yêu Cầu Hỗ Trợ','Bắt đầu cuộc tư vấn');w('Views/Home/Contact.cshtml',s)
s=r('Views/Home/Index.cshtml');a=s.index('                                        <button type="button" class="btn btn-light border');b=s.index('                                        </button>',a)+len('                                        </button>');s=s[:a]+'''                                        <a asp-controller="Home" asp-action="Contact" class="btn btn-light border fw-semibold px-3 py-2 btn-sm rounded-3 text-dark"><i class="fa-solid fa-comments me-1 text-primary"></i> Nhắn tin tư vấn</a>'''+s[b:];a=s.index('<!-- Modal Consultation Form -->');s=s[:a];w('Views/Home/Index.cshtml',s)
s=r('Views/Shared/_Layout.cshtml');needle='                                    <li><a class="dropdown-item py-2" asp-area="" asp-controller="Student" asp-action="Profile"';at=s.index(needle);s=s[:at]+'''                                    <li><a class="dropdown-item py-2" asp-area="" asp-controller="Consultation" asp-action="Mine"><i class="fa-solid fa-comments me-2 text-primary"></i> Tư vấn của tôi</a></li>
'''+s[at:];w('Views/Shared/_Layout.cshtml',s)
print('Live chat UI, admin inbox, contact form and navigation updated')
