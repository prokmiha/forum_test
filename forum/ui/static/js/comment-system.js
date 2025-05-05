import { CommentService } from './services/commentService.js';
import { FileService } from './services/fileService.js';
import { CommentComponent } from './components/commentComponent.js';
import { FormComponent } from './components/formComponent.js';
import { Validation } from './validation.js';
import { AttachmentManager } from './services/attachmentManager.js';

document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        commentText: document.getElementById('comment-text'),
        userName: document.getElementById('user-name'),
        userEmail: document.getElementById('user-email'),
        submitComment: document.getElementById('submit-comment'),
        commentsList: document.getElementById('comments-list'),
        fileUpload: document.getElementById('file-upload'),
        attachmentsPreview: document.getElementById('attachments-preview'),
        csrfToken: document.querySelector('[name=csrfmiddlewaretoken]').value,
        captchaModal: document.getElementById('captcha-modal'),
        captchaImg: document.getElementById('captcha-img'),
        captchaInput: document.getElementById('captcha-input'),
        confirmCaptcha: document.getElementById('confirm-captcha'),
        refreshCaptcha: document.getElementById('refresh-captcha'),
        closeCaptcha: document.getElementById('close-captcha')
    };

    let state = {
        attachments: [],
        captchaContext: null,
        pendingPayload: null
    };

    initializeApp();

    async function initializeApp() {
        try {
            const data = await CommentService.fetchComments();
            CommentComponent.renderCommentsList(data.results, elements.commentsList);
            bindEvents();
        } catch (err) {
            console.error("Ошибка при инициализации:", err);
        }
    }

    function bindEvents() {
        elements.submitComment.addEventListener('click', () => handleCommentSubmit());
        elements.commentsList.addEventListener('click', handleCommentActions);

        elements.fileUpload.addEventListener('change', handleFileUpload);

        elements.confirmCaptcha.addEventListener('click', handleCaptchaConfirm);
        elements.refreshCaptcha.addEventListener('click', () => {
            elements.captchaImg.src = FileService.refreshCaptcha();
        });
        elements.closeCaptcha.addEventListener('click', FormComponent.hideCaptchaModal);
        FormComponent.initTagButtons(elements);
    }

    function handleCommentActions(e) {
        if (e.target.classList.contains('reply-button')) {
            const commentId = e.target.dataset.commentId;
            CommentComponent.clearReplyForms();
            e.target.style.display = "none";
            const replyForm = FormComponent.createReplyForm(commentId);
            FormComponent.initTagButtons(elements);
            e.target.closest(".comment-content-part").after(replyForm);

            const fileUpload = replyForm.querySelector('.reply-file-upload');
            const fileLabel = replyForm.querySelector('.file-upload-label');
            
            fileLabel.addEventListener('click', () => {
                fileUpload.click();
            });
            
            fileUpload.addEventListener('change', handleFileUpload);
        } else if (e.target.classList.contains('submit-reply')) {
            handleReplySubmit(e);
        } else if (e.target.classList.contains('cancel-reply')) {
            FormComponent.handleReplyCancel(e);
        } else if (e.target.classList.contains('load-more-replies')) {
            CommentComponent.handleLoadMoreReplies(e, CommentService);
        } else if (e.target.classList.contains('show-discussion-button')) {
            CommentComponent.handleShowDiscussion(e, CommentService);
        }
    }

    function validateForm() {
        try {
            if (!elements.commentText.value.trim() || 
                !elements.userName.value.trim() || 
                !elements.userEmail.value.trim()) {
                throw new Error("Пожалуйста, заполните все обязательные поля");
            }

            Validation.username(elements.userName.value);
            Validation.email(elements.userEmail.value);
            
            return true;
        } catch (err) {
            alert(err.message);
            return false;
        }
    }

    function handleCommentSubmit() {
        if (!validateForm()) return;

        state.captchaContext = "root";
        state.pendingPayload = {
            user_name: elements.userName.value,
            email: elements.userEmail.value,
            homepage: "",
            text: elements.commentText.value,
            parent: null
        };

        const fileInput = elements.fileUpload;
        if (fileInput && fileInput.files) {
            state.attachments = Array.from(fileInput.files);
        }    

        FormComponent.showCaptchaModal();
    }

    function handleReplySubmit(event) {
        const submitButton = event.target;
        const parentId = parseInt(submitButton.dataset.parentId, 10);
        const replyForm = submitButton.closest('.reply-form');
        
        const text = replyForm.querySelector('.reply-text').value;
        const userName = replyForm.querySelector('.reply-name').value;
        const email = replyForm.querySelector('.reply-email').value;

        try {
            if (!text.trim() || !userName.trim() || !email.trim()) {
                throw new Error("Пожалуйста, заполните все обязательные поля");
            }

            Validation.username(userName);
            Validation.email(email);

            state.captchaContext = "reply";
            state.pendingPayload = {
                text: text,
                user_name: userName,
                email: email,
                parent: parentId
            };

            const fileInput = replyForm.querySelector('.reply-file-upload');
            if (fileInput && fileInput.files) {
                state.attachments = Array.from(fileInput.files);
            }

            FormComponent.showCaptchaModal();
        } catch (err) {
            alert(err.message);
        }
    }

    let uploadedFiles = [];

    function handleFileUpload(event) {
        const newFiles = Array.from(event.target.files);

        if (uploadedFiles.length + newFiles.length > 5) {
            alert('Можно загрузить не более 5 файлов');
            return;
        }

        uploadedFiles.push(...newFiles);
        event.target.value = '';
        renderPreview();
    }

    function renderPreview() {
        const previewContainer = document.querySelector('.attachments-preview');
        const fileInput = document.querySelector('input[type="file"]');
        previewContainer.innerHTML = '';

        uploadedFiles.forEach((file, index) => {
            const preview = document.createElement('div');
            preview.className = 'file-preview';

            if (file.type.startsWith('image/')) {
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.onload = () => URL.revokeObjectURL(img.src);
                preview.appendChild(img);
            } else {
                const icon = document.createElement('i');
                icon.className = 'fas fa-file-alt';
                preview.appendChild(icon);
            }

            const fileName = document.createElement('span');
            fileName.textContent = file.name;
            preview.appendChild(fileName);

            const removeBtn = document.createElement('button');
            removeBtn.className = 'remove-file';
            removeBtn.innerHTML = '&times;';
            removeBtn.onclick = () => {
                uploadedFiles.splice(index, 1);
                renderPreview();
            };
            preview.appendChild(removeBtn);
            previewContainer.appendChild(preview);
        });

        const dataTransfer = new DataTransfer();
        uploadedFiles.forEach(file => dataTransfer.items.add(file));
        fileInput.files = dataTransfer.files;
    }

    async function handleCaptchaConfirm() {
        if (!state.pendingPayload) return;
    
        const formData = new FormData();
        Object.entries(state.pendingPayload).forEach(([key, value]) => {
            if (value !== null) formData.append(key, value);
        });
        formData.append("captcha_value", elements.captchaInput.value);
    
        if (state.attachments && state.attachments.length > 0) {
            state.attachments.forEach(file => {
                formData.append('attachments', file);
            });
        }
    
        try {
            let data;
            if (state.captchaContext === "reply") {
                const parentId = state.pendingPayload.parent;
                data = await CommentService.postReply(parentId, formData, elements.csrfToken);
                
                const parentElement = document.querySelector(`[data-comment-id="${parentId}"]`);
                if (parentElement) {
                    let repliesContainer = parentElement.querySelector(`.replies[data-parent-id="${parentId}"]`);

                    if (!repliesContainer) {
                        repliesContainer = document.createElement('div');
                        repliesContainer.className = 'replies';
                        repliesContainer.dataset.parentId = parentId;
                        parentElement.appendChild(repliesContainer);
                    }

                    const replyElement = CommentComponent.renderComment(data);
                    repliesContainer.insertBefore(replyElement, repliesContainer.firstChild);
                } else {
                    console.warn("Parent not found in DOM. Skipping dynamic render.");
                }

                const replyForm = document.querySelector(`.reply-form[data-parent-id="${parentId}"]`);
                if (replyForm) {
                    const commentBlock = replyForm.closest('.comment, .reply');
                    const replyButton = commentBlock.querySelector('.reply-button');
                    replyForm.remove();
                    if (replyButton) {
                        replyButton.style.display = "inline";
                    }
                }
            } else {
                data = await CommentService.postComment(formData, elements.csrfToken);
                FormComponent.clearForm(elements);
                elements.commentsList.prepend(CommentComponent.renderComment(data));
            }
    
            FormComponent.hideCaptchaModal();
    
            state.attachments = [];
            FileService.updateAttachmentsPreview(state.attachments, elements.attachmentsPreview);
    
            state = {
                attachments: [],
                captchaContext: null,
                pendingPayload: null
            };

            resetFileUpload();
        } catch (err) {
            alert(err.message);
            elements.captchaInput.value = ""
            elements.captchaImg.src = FileService.refreshCaptcha();
        }
    }
    
    window.handleRemoveFile = (fileId) => {
        state.attachments = FileService.removeFile(fileId, state.attachments);
        FileService.updateAttachmentsPreview(state.attachments, elements.attachmentsPreview);
    };

    function resetFileUpload() {
    uploadedFiles = [];
    const fileInput = document.querySelector('input[type="file"]');
    const previewContainer = document.querySelector('.attachments-preview');

    const dataTransfer = new DataTransfer();
    fileInput.files = dataTransfer.files;

    previewContainer.innerHTML = '';
    }
}); 