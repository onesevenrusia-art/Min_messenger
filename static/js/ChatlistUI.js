export function createChatElement(chat) {
    const div = document.createElement("div");
    div.dataset.chatId = chat.id;
    div.className = "chatinfo";
    const img = document.createElement("img");
    img.className = "chat-avatar";
    img.src = chat.photo;
    img.alt = "";
    img.style.marginLeft = "12px";
    const name = document.createElement("b");
    name.className = "chat-name";
    name.textContent = chat.name;
    const unread = 0;
    div.append(img);
    div.append(name);
    if (unread instanceof HTMLElement)
        div.append(unread);
    else
        div.insertAdjacentHTML("beforeend", unread);
    return div;
}

export function add(chat){
    const chatElement = createChatElement(chat);
    ChatBox.append(chatElement);
}

export function remove(id){
    document.querySelector(`[data-chat-id="${id}"]`)?.remove();
}

export function update(id, name=null, avatar=null, unread=false){
    const chat = document.querySelector(`[data-chat-id="${id}"]`);
    if (name !== null){
        chat.querySelector(".chat-name").textContent = name;
    }
    if (avatar !== null){
        chat.querySelector(".chat-avatar").src = avatar;
    }
    if (unread !== null){
        
    }
}