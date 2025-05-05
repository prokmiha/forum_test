export class FileService {
    static MAX_FILES = 5;

    static validateFile(file) {
        const allowedImageTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const allowedTextTypes = ['text/plain'];
        
        if (!allowedImageTypes.includes(file.type) && !allowedTextTypes.includes(file.type)) {
            throw new Error("Неподдерживаемый формат файла");
        }

        if (file.type === 'text/plain' && file.size > 100 * 1024) {
            throw new Error("Размер текстового файла не должен превышать 100KB");
        }

        if (allowedImageTypes.includes(file.type) && file.size > 5 * 1024 * 1024) {
            throw new Error("Размер изображения не должен превышать 5MB");
        }

        return true;
    }

    static refreshCaptcha() {
        return `/captcha/?${Date.now()}`;
    }

    static handleFileUpload(files, attachments = []) {
        if (attachments.length + files.length > this.MAX_FILES) {
            throw new Error(`Максимальное количество файлов: ${this.MAX_FILES}`);
        }

        const validatedFiles = [];
        
        try {
            files.forEach(file => {
                if (this.validateFile(file)) {
                    validatedFiles.push({
                        id: Date.now() + Math.random().toString(36).substr(2, 9),
                        file: file
                    });
                }
            });
            return [...attachments, ...validatedFiles];
        } catch (err) {
            throw new Error(err.message);
        }
    }

    static removeFile(fileId, attachments) {
        return attachments.filter(attachment => attachment.id !== fileId);
    }

    static updateAttachmentsPreview(attachments, previewElement) {
        previewElement.innerHTML = attachments
            .map(attachment => `
                <div class="attachment-item" data-file-id="${attachment.id}">
                    <span class="file-name" title="${attachment.file.name}">${attachment.file.name}</span>
                    <button class="remove-file" onclick="window.handleRemoveFile('${attachment.id}')">
                        ✕
                    </button>
                </div>
            `)
            .join('');
    }

    static appendToFormData(formData, attachments) {
        attachments.forEach(attachment => {
            formData.append("attachments", attachment.file);
        });
        return formData;
    }
} 