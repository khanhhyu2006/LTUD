(() => {
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
            const wasClosed=closed;closed=data.status==='Closed';controls.forEach(e=>e.disabled=closed||sending);
            if(closed)feedback.textContent='Cuộc tư vấn đã kết thúc. Bạn có thể gửi yêu cầu mới từ trang liên hệ.';
            else if(wasClosed)feedback.textContent='Cuộc tư vấn đã được mở lại. Bạn có thể tiếp tục nhắn tin.';
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
