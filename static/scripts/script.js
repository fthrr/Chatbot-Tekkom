const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");

var nama;
var count_global;
var pertanyaan_global;
var input;
var jawaban;

function appendMessage(name, img, side, text) {
    //   Simple solution for small apps
    const msgHTML = `
        <div class="msg ${side}-msg">
            <div class="msg-img" style="background-image: url(${img})"></div>
            <div class="msg-bubble">
                <div class="msg-info">
                <div class="msg-info-name">${name}</div>
                <div class="msg-info-time">${formatDate(new Date())}</div>
            </div>
            <div class="msg-text">${text}</div>
            </div>
        </div>`;

    msgerChat.insertAdjacentHTML("beforeend", msgHTML);
    msgerChat.scrollTop += 500;
}

//====================================================================================================================//
nama = prompt("Masukkan nama kamu: ");
while (nama.trim() === "") {
    nama = prompt("Masukkan nama Kamu:");
    if (nama.trim() !== "") {
        nama = nama;
    }
}
//====================================================================================================================//

const BOT_IMG =
    "./static/image/bot.jpg";
const PERSON_IMG =
    "./static/image/person.jpg";
const BOT_NAME = "    Tekkom Bot \uD83D\uDE3B";
const PERSON_NAME = nama;

function botResponse(nama, rawText) {
    $.get("/post", { nama: nama, msg: rawText }).done(function (data) {
        const msgText = data;
        appendMessage(BOT_NAME, BOT_IMG, "left", msgText);

        if (rawText.toLowerCase() == "ga" || 
            rawText.toLowerCase() == "tidak" ||
            rawText.toLowerCase() == "gak" ||
            rawText.toLowerCase() == "g") {
                document.getElementById("textInput").disabled = true;
                document.getElementById("textInput").placeholder = "Silahkan refresh browser jika ingin bertanya kembali";
        } else {
            text_sekian =
                "Ada yang ingin kamu tanyakan lagi terkait akademis di Teknik Komputer FTUI?";
            appendMessage(BOT_NAME, BOT_IMG, "left", text_sekian);
        }
    });
}
   
msgerForm.addEventListener("submit", (event) => {
    event.preventDefault();
      
    const msgText = msgerInput.value;
    const nama = PERSON_NAME;

    if (!msgText) return;
        
    appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText);
        
    msgerInput.value = "";

    if (msgText.toLowerCase() === "ga" || 
            msgText.toLowerCase() === "tidak" ||
            msgText.toLowerCase() === "gak") {
            document.getElementById("textInput").disabled = true;
            document.getElementById("textInput").placeholder = "Silahkan refresh browser jika ingin bertanya kembali";
        }

    botResponse(nama, msgText)
    window.input = msgText
});

// =========================================================================================== //

nama_greet = nama.toLowerCase().replace(/\w/, (firstLetter) => firstLetter.toUpperCase());
text_satu =
    "Halo " + nama_greet + ", selamat datang di Tekkom Chatbot! 😄";
text_dua =
    "Ada yang ingin kamu tanyakan terkait akademis di Teknik Komputer FTUI? Silahkan masukan pertanyaanmu";

appendMessage(BOT_NAME, BOT_IMG, "left", text_satu);
appendMessage(BOT_NAME, BOT_IMG, "left", text_dua);

const divroom = document.getElementsByClassName(".msmsger-chat");
divroom.scrollTop = 0;


// =========================================================================================== //

// Utils
function get(selector, root = document) {
    return root.querySelector(selector);
}
    
function formatDate(date) {
    const h = "0" + date.getHours();
    const m = "0" + date.getMinutes();

    return `${h.slice(-2)}:${m.slice(-2)}`;
}