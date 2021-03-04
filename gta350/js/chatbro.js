function ChatbroLoader(chats, async) {
  async = async || true;
  var params = {  
    embedChatsParameters: chats instanceof Array ? chats : [chats], 
    needLoadCode: typeof Chatbro === "undefined"
  }; 
  var xhr = new XMLHttpRequest();
  xhr.withCredentials = true;
  xhr.onload = function() {
    eval(xhr.responseText);
  };
  xhr.onerror = function() {
    console.error("Chatbro loading error");
  };
  xhr.open("POST", "https://www.chatbro.com/embed_chats", async);
  xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
  xhr.send("parameters=" + encodeURIComponent(JSON.stringify(params)));
}

function loadChatbro(chatId) {
  ChatbroLoader({  
    encodedChatId: chatId,
    containerDivId: 'testChat',
    chatLanguage: 'en',
    showChatMenu: false,  
    showHelpMessages: false,
    minimizedChatRight: '50%'
  })
}

var showStateContainer = document.getElementsByClassName('message')[0];

document.addEventListener('chatLoaded', function() {
  document.addEventListener('maximizeChat', function() {
    showStateContainer.innerHTML = 'maximizeChat'; 
  });
  
  document.addEventListener('minimizeChat', function() {
    showStateContainer.innerHTML = 'minimizeChat'; 
  });
});