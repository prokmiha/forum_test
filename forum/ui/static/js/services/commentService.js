export const CommentService = {
    async fetchComments() {
        const response = await fetch("/api/comment/");
        if (!response.ok) throw new Error("Ошибка загрузки комментариев");
        return response.json();
    },

    async postComment(formData, csrfToken) {
        const response = await fetch("/api/comment/", {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Ошибка при отправке");
        }
        return response.json();
    },

    async loadReplies(parentId, offset = 0, limit = 3) {
        const response = await fetch(`/comment/${parentId}/replies/?offset=${offset}&limit=${limit}`);
        if (!response.ok) throw new Error("Ошибка загрузки ответов");
        return response.json();
    },

    async postReply(parentId, formData, csrfToken) {
        const response = await fetch(`/comment/${parentId}/replies/`, {
            method: "POST",
            headers: { "X-CSRFToken": csrfToken },
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || "Ошибка при отправке ответа");
        }
        return response.json();
    }
}; 