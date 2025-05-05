import {FileService} from './fileService.js';

export class AttachmentManager {
    constructor(fileInputSelector, previewSelector) {
        this.fileInput = document.querySelector(fileInputSelector);
        this.previewElement = document.querySelector(previewSelector);
        this.attachments = [];
        
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        this.fileInput.addEventListener('change', (e) => this.handleFileSelection(e));
    }

    handleFileSelection(event) {
        try {
            this.attachments = FileService.handleFileUpload(
                Array.from(event.target.files),
                this.attachments
            );
            this.updatePreview();
            event.target.value = '';
        } catch (error) {
            this.showError(error.message);
        }
    }

    updatePreview() {
        FileService.updateAttachmentsPreview(this.attachments, this.previewElement);
        this.setupRemoveHandlers();
    }

    setupRemoveHandlers() {
        this.previewElement.querySelectorAll('.remove-file').forEach(button => {
            button.onclick = (e) => {
                e.preventDefault();
                const fileId = button.parentElement.dataset.fileId;
                this.removeFile(fileId);
            };
        });
    }

    removeFile(fileId) {
        this.attachments = FileService.removeFile(fileId, this.attachments);
        this.updatePreview();
    }

    getAttachments() {
        return this.attachments;
    }

    clearAttachments() {
        this.attachments = [];
        this.updatePreview();
    }

    showError(message) {
        alert(message);
    }

    appendToFormData(formData) {
        return FileService.appendToFormData(formData, this.attachments);
    }
}