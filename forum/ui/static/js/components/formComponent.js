export class FormComponent {
    static createReplyForm(commentId) {
        const form = document.createElement("div");
        form.classList.add("reply-form");
        form.dataset.parentId = commentId;
        form.innerHTML = `
            <textarea class="reply-text comment-textarea" placeholder="Введите ваш ответ..."></textarea>
            <div class="user-info">
                <input type="text" class="reply-name" placeholder="Ваше имя">
                <input type="email" class="reply-email" placeholder="Email">
            </div>
            <div class="attachments-section">
                <label class="file-upload-label">
                    <i class="fas fa-paperclip"></i>
                    <span>Прикрепить файл</span>
                </label>
                <input type="file" class="reply-file-upload" multiple accept="image/jpeg,image/png,image/gif,text/plain" style="display: none;">
                <div class="reply-attachments-preview attachments-preview"></div>
            </div>
            <div style="display: flex; gap: 10px; margin-top: 10px;">
                <button class="submit-reply submit-button" data-parent-id="${commentId}">Ответить</button>
                <button class="cancel-reply action-button">Отменить</button>
            </div>
        `;
        return form;
    }

    static initTagButtons(elements) {
        document.getElementById('insert-italic').addEventListener('click', () => {
            FormComponent.insertTag(elements.commentText, 'i');
        });
    
        document.getElementById('insert-bold').addEventListener('click', () => {
            FormComponent.insertTag(elements.commentText, 'strong');
        });
    
        document.getElementById('insert-code').addEventListener('click', () => {
            FormComponent.insertTag(elements.commentText, 'code');
        });
    
        document.getElementById('insert-link').addEventListener('click', () => {
            const textarea = elements.commentText;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const selectedText = textarea.value.slice(start, end);

            let href = prompt('Введите ссылку:', 'https://');
            if (!href) return;

            if (!href.startsWith('http://') && !href.startsWith('https://')) {
                href = 'https://' + href;
            }

            let linkText = selectedText;
            if (start === end) { // Если нет выделения
                linkText = prompt('Введите текст ссылки:', href);
                if (!linkText) return;
            }

            const openTag = `<a href="${href}" title="${linkText}">`;
            const closeTag = `</a>`;

            textarea.value = textarea.value.slice(0, start) + openTag + linkText + closeTag + textarea.value.slice(end);

            const cursorPosition = start + openTag.length;
            textarea.setSelectionRange(cursorPosition, cursorPosition + linkText.length);
            textarea.focus();
        });
    }

    static showCaptchaModal() {
        const modal = document.getElementById("captcha-modal");
        const img = document.getElementById("captcha-img");
        img.src = `/captcha/?${Date.now()}`;
        modal.style.display = "flex";
    }

    static hideCaptchaModal() {
        const modal = document.getElementById("captcha-modal");
        modal.style.display = "none";
        document.getElementById("captcha-input").value = "";
    }

    static validateForm(elements) {
        if (!elements.commentText.value.trim() || 
            !elements.userName.value.trim() || 
            !elements.userEmail.value.trim()) {
            throw new Error("Пожалуйста, заполните все обязательные поля");
        }
        return true;
    }

    static getFormData(elements, context = "root") {
        return {
            user_name: context === "root" ? elements.userName.value : elements.querySelector('.reply-name').value,
            email: context === "root" ? elements.userEmail.value : elements.querySelector('.reply-email').value,
            homepage: "",
            text: context === "root" ? elements.commentText.value : elements.querySelector('.reply-text').value,
            parent: context === "root" ? null : elements.querySelector('.submit-reply').dataset.parentId
        };
    }

    static clearForm(elements) {
        elements.commentText.value = "";
        elements.userName.value = "";
        elements.userEmail.value = "";
    }

    static handleReplyCancel(e) {
        const form = e.target.closest('.reply-form');
        const commentBlock = form.closest('.comment, .reply');
        form.remove();
        commentBlock.querySelector('.reply-button').style.display = "inline";
    }

    static insertTag(textarea, tagName, options = {}) {
        const { href = "", title = "" } = options;
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const text = textarea.value;
    
        let openTag = `<${tagName}>`;
        let closeTag = `</${tagName}>`;
    
        if (tagName === "a") {
            openTag = `<a href="${href}" title="${title}">`;
            closeTag = `</a>`;
        }
    
        const selectedText = text.slice(start, end);
    
        const newText = text.slice(0, start) + openTag + selectedText + closeTag + text.slice(end);
    
        textarea.value = newText;
    
        const cursorPosition = start + openTag.length;
        textarea.setSelectionRange(cursorPosition, cursorPosition + selectedText.length);
        textarea.focus();
    }    
} 