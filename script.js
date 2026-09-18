const chatForm = document.getElementById("chatForm");
const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");

const messages = document.getElementById("messages");
const welcomeScreen = document.getElementById("welcomeScreen");

const newChatBtn = document.getElementById("newChatBtn");
const pdfInput = document.getElementById("pdfInput");
const reindexBtn = document.getElementById("reindexBtn");

const statusText = document.getElementById("statusText");
const knowledgeStatus = document.getElementById("knowledgeStatus");

const toast = document.getElementById("toast");
const uploadNotice = document.getElementById("uploadNotice");


/* ============================================================
   UTILITIES
   ============================================================ */

function escapeHTML(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


function formatAnswer(text) {
    let safe = escapeHTML(text);

    safe = safe.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    safe = safe.replace(
        /\n/g,
        "<br>"
    );

    return safe;
}


function getTime() {
    return new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}


function showToast(message) {
    toast.textContent = message;
    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}


/* ============================================================
   ADD MESSAGE
   ============================================================ */

function addMessage(
    role,
    text,
    sources = []
) {

    welcomeScreen.style.display = "none";

    const wrapper = document.createElement("div");

    wrapper.className = `message ${role}`;

    const avatar = document.createElement("div");

    avatar.className =
        `message-avatar ${
            role === "assistant"
                ? "ai-avatar"
                : "user-avatar"
        }`;

    avatar.textContent =
        role === "assistant"
            ? "✦"
            : "YOU";


    const content = document.createElement("div");

    content.className = "message-content";


    const bubble = document.createElement("div");

    bubble.className = "message-bubble";

    bubble.innerHTML =
        role === "assistant"
            ? formatAnswer(text)
            : escapeHTML(text);


    const time = document.createElement("div");

    time.className = "message-time";

    time.textContent = getTime();


    content.appendChild(bubble);
    content.appendChild(time);


    if (sources.length > 0) {

        const sourceContainer =
            document.createElement("div");

        sourceContainer.className = "sources";


        sources.forEach(source => {

            const sourceElement =
                document.createElement("span");

            sourceElement.className = "source";

            let label = source.source || "Knowledge Base";

            if (source.page) {
                label += ` • Page ${source.page}`;
            }

            sourceElement.textContent =
                `Source: ${label}`;

            sourceContainer.appendChild(
                sourceElement
            );

        });


        content.appendChild(sourceContainer);
    }


    if (role === "assistant") {

        wrapper.appendChild(avatar);
        wrapper.appendChild(content);

    } else {

        wrapper.appendChild(content);
        wrapper.appendChild(avatar);

    }


    messages.appendChild(wrapper);

    scrollToBottom();
}


/* ============================================================
   TYPING INDICATOR
   ============================================================ */

function showTyping() {

    const wrapper =
        document.createElement("div");

    wrapper.className = "message assistant";

    wrapper.id = "typingMessage";


    const avatar =
        document.createElement("div");

    avatar.className =
        "message-avatar ai-avatar";

    avatar.textContent = "✦";


    const content =
        document.createElement("div");

    content.className = "message-content";


    const bubble =
        document.createElement("div");

    bubble.className = "message-bubble";


    const typing =
        document.createElement("div");

    typing.className = "typing";

    typing.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;


    bubble.appendChild(typing);
    content.appendChild(bubble);

    wrapper.appendChild(avatar);
    wrapper.appendChild(content);

    messages.appendChild(wrapper);

    scrollToBottom();
}


function removeTyping() {

    const typing =
        document.getElementById(
            "typingMessage"
        );

    if (typing) {
        typing.remove();
    }
}


/* ============================================================
   SCROLL
   ============================================================ */

function scrollToBottom() {

    const container =
        document.getElementById(
            "chatContainer"
        );

    setTimeout(() => {

        container.scrollTo({
            top: container.scrollHeight,
            behavior: "smooth"
        });

    }, 50);
}


/* ============================================================
   SEND QUESTION
   ============================================================ */

async function sendQuestion(question) {

    question = question.trim();

    if (!question) {
        return;
    }


    addMessage(
        "user",
        question
    );


    questionInput.value = "";

    autoResize();


    sendBtn.disabled = true;

    showTyping();


    try {

        const response =
            await fetch(
                "/api/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        question: question
                    })
                }
            );


        const data =
            await response.json();


        removeTyping();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to get a response."
            );
        }


        addMessage(
            "assistant",
            data.answer,
            data.sources || []
        );


    } catch (error) {

        removeTyping();

        addMessage(
            "assistant",
            `I couldn't process your request. ${error.message}`
        );

    } finally {

        sendBtn.disabled = false;

        questionInput.focus();
    }
}


/* ============================================================
   CHAT FORM
   ============================================================ */

chatForm.addEventListener(
    "submit",
    event => {

        event.preventDefault();

        sendQuestion(
            questionInput.value
        );

    }
);


/* ============================================================
   ENTER TO SEND
   ============================================================ */

questionInput.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            chatForm.requestSubmit();
        }

    }
);


/* ============================================================
   AUTO RESIZE TEXTAREA
   ============================================================ */

function autoResize() {

    questionInput.style.height = "auto";

    questionInput.style.height =
        Math.min(
            questionInput.scrollHeight,
            110
        ) + "px";
}


questionInput.addEventListener(
    "input",
    autoResize
);


/* ============================================================
   SUGGESTED QUESTIONS
   ============================================================ */

document
    .querySelectorAll(".suggestion")
    .forEach(button => {

        button.addEventListener(
            "click",
            () => {

                const question =
                    button.dataset.question;

                sendQuestion(question);

            }
        );

    });


/* ============================================================
   NEW CHAT
   ============================================================ */

newChatBtn.addEventListener(
    "click",
    () => {

        messages.innerHTML = "";

        welcomeScreen.style.display =
            "flex";

        questionInput.value = "";

        uploadNotice.textContent = "";

        questionInput.focus();

    }
);


/* ============================================================
   HEALTH CHECK
   ============================================================ */

async function checkHealth() {

    try {

        const response =
            await fetch(
                "/api/health"
            );

        if (!response.ok) {
            throw new Error();
        }

        const data =
            await response.json();

        statusText.textContent =
            "FastAPI backend online";

        knowledgeStatus.textContent =
            "Knowledge base ready";

    } catch {

        statusText.textContent =
            "Backend unavailable";

        knowledgeStatus.textContent =
            "Check server connection";
    }
}


/* ============================================================
   PDF UPLOAD
   ============================================================ */

pdfInput.addEventListener(
    "change",
    async () => {

        const file =
            pdfInput.files[0];

        if (!file) {
            return;
        }


        if (
            file.type !== "application/pdf" &&
            !file.name.toLowerCase().endsWith(".pdf")
        ) {

            showToast(
                "Please select a PDF file."
            );

            pdfInput.value = "";

            return;
        }


        const formData =
            new FormData();

        formData.append(
            "file",
            file
        );


        uploadNotice.textContent =
            `Uploading ${file.name}...`;


        try {

            const response =
                await fetch(
                    "/api/upload",
                    {
                        method: "POST",
                        body: formData
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Upload failed."
                );
            }


            uploadNotice.textContent =
                `${file.name} uploaded. Reindex the knowledge base to use it.`;


            showToast(
                "PDF uploaded successfully."
            );


        } catch (error) {

            uploadNotice.textContent = "";

            showToast(
                error.message
            );

        } finally {

            pdfInput.value = "";
        }

    }
);


/* ============================================================
   REINDEX
   ============================================================ */

reindexBtn.addEventListener(
    "click",
    async () => {

        reindexBtn.disabled = true;

        reindexBtn.textContent =
            "Reindexing...";


        try {

            const response =
                await fetch(
                    "/api/reindex",
                    {
                        method: "POST"
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Reindexing failed."
                );
            }


            knowledgeStatus.textContent =
                `${data.chunks} knowledge chunks`;


            showToast(
                `Knowledge base updated: ${data.chunks} chunks`
            );


        } catch (error) {

            showToast(
                error.message
            );

        } finally {

            reindexBtn.disabled = false;

            reindexBtn.textContent =
                "↻ Reindex Knowledge Base";
        }

    }
);


/* ============================================================
   INITIALIZE
   ============================================================ */

checkHealth();

questionInput.focus();
