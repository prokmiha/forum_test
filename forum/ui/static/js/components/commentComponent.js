export class CommentComponent {
    static renderComment(comment) {
        if (!comment) return null;

        const commentElement = document.createElement('div');
        commentElement.className = comment.parent ? 'reply' : 'comment';
        commentElement.dataset.commentId = comment.id;

        const attachmentsHtml = comment.attachments?.length 
            ? this.renderAttachments(comment.attachments)
            : '';
        const repliesHtml = this.renderReplies(comment);

        commentElement.innerHTML = `
            <div class="comment-content-part">
                <div class="comment-header">
                    <span class="user-name">${comment.user_name}</span>
                    <span class="comment-date">${new Date(comment.created_at).toLocaleString()}</span>
                </div>
                <div class="comment-text">${comment.text}</div>
                ${attachmentsHtml}
                <div class="comment-actions">
                    <button class="reply-button" data-comment-id="${comment.id}">Ответить</button>
                </div>
            </div>
            ${repliesHtml}
        `;

        return commentElement;
    }

    static renderAttachments(attachments) {
        if (!attachments?.length) return '';

        return `
            <div class="comment-attachments">
                ${attachments.map(attachment => {
                    if (!attachment?.file) return '';

                    if (attachment.file_type === 'image') {
                        return `
                            <div class="attachment-preview">
                                <a href="${attachment.file}" target="_blank">
                                    <img src="${attachment.file}" alt="Изображение" loading="lazy">
                                </a>
                            </div>
                        `;
                    } else {
                        const fileName = attachment.file.split('/').pop();
                        return `
                            <div class="attachment-file">
                                <a href="${attachment.file}" target="_blank" class="file-link">
                                    <i class="fas fa-file-alt"></i>
                                    ${fileName}
                                </a>
                            </div>
                        `;
                    }
                }).join('')}
            </div>
        `;
    }

    static renderReplies(comment) {
        const replies = comment.replies || [];
        let html = `<div class="replies" data-parent-id="${comment.id}">`;

        replies.forEach(reply => {
            const replyElement = this.renderComment(reply);
            if (replyElement) {
                html += replyElement.outerHTML;
            }
        });

        html += '</div>';

        if (!comment.parent) {
            if (comment.reply_count > replies.length) {
                const remaining = comment.reply_count - replies.length;
                html += `
                    <button class="action-button load-more-replies" 
                            data-parent-id="${comment.id}" 
                            data-offset="${replies.length}">
                        Показать ещё комментарии (${remaining})
                    </button>
                `;
            }
        } else {
            if (comment.reply_count > 0 && replies.length === 0) {
                html += `
                    <button class="action-button show-discussion-button" 
                            data-parent-id="${comment.id}" 
                            data-offset="0">
                        Посмотреть обсуждение (${comment.reply_count})
                    </button>
                `;
            }
        }

        return html;
    }

    static async handleLoadMoreReplies(e, commentService) {
        const btn = e.target;
        const parentId = btn.dataset.parentId;
        const parentComment = document.querySelector(`[data-comment-id="${parentId}"]`);
        const offset = parseInt(btn.dataset.offset, 10) || 0;
        const limit = 3;

        try {
            const data = await commentService.loadReplies(parentId, offset, limit);
            let repliesContainer = parentComment.querySelector(`.replies[data-parent-id="${parentId}"]`);

            if (!repliesContainer) {
                repliesContainer = document.createElement('div');
                repliesContainer.className = 'replies';
                repliesContainer.dataset.parentId = parentId;
                parentComment.appendChild(repliesContainer);
            }

            data.results.forEach(reply => {
                reply.replies = [];
                const replyElement = CommentComponent.renderComment(reply);
                repliesContainer.appendChild(replyElement);
            });

            if (data.has_more) {
                btn.dataset.offset = offset + limit;
                const remaining = data.total - (offset + limit);
                btn.textContent = `Показать ещё комментарии (${remaining})`;
            } else {
                btn.remove();
            }
        } catch (err) {
            console.error("Ошибка при загрузке комментариев:", err);
        }
    }

    static async handleShowDiscussion(e, commentService) {
        const btn = e.target;
        const parentId = btn.dataset.parentId;
        const offset = 0;
        const limit = 3;

        try {
            const data = await commentService.loadReplies(parentId, offset, limit);
            const parentComment = document.querySelector(`[data-comment-id="${parentId}"]`);

            let repliesContainer = parentComment.querySelector(`.replies[data-parent-id="${parentId}"]`);
            if (!repliesContainer) {
                repliesContainer = document.createElement('div');
                repliesContainer.className = 'replies';
                repliesContainer.dataset.parentId = parentId;
                parentComment.appendChild(repliesContainer);
            }

            data.results.forEach(reply => {
                reply.replies = [];
                const replyElement = CommentComponent.renderComment(reply);
                repliesContainer.appendChild(replyElement);
            });

            btn.remove();

            if (data.has_more) {
                const loadMoreBtn = document.createElement('button');
                loadMoreBtn.className = 'action-button load-more-replies';
                loadMoreBtn.dataset.parentId = parentId;
                loadMoreBtn.dataset.offset = offset + limit;
                loadMoreBtn.textContent = `Показать ещё комментарии (${data.total - (offset + limit)})`;
                repliesContainer.appendChild(loadMoreBtn);
            }
        } catch (error) {
            console.error("Ошибка при загрузке обсуждения:", error);
        }
    }

    static appendReplyToParent(parentId, replyData) {
        const parentComment = document.querySelector(`[data-comment-id="${parentId}"]`);
        let repliesContainer = parentComment.querySelector('.replies');

        if (!repliesContainer) {
            repliesContainer = document.createElement('div');
            repliesContainer.classList.add('replies');
            repliesContainer.dataset.parentId = parentId;
            parentComment.appendChild(repliesContainer);
        }

        repliesContainer.appendChild(this.renderComment(replyData));
    }

    static clearReplyForms() {
        document.querySelectorAll(".reply-form").forEach(form => {
            const commentBlock = form.closest('.comment, .reply');
            form.remove();
            commentBlock.querySelector('.reply-button').style.display = "inline";
        });
    }

    static renderCommentsList(comments, container) {
        container.innerHTML = "";
        comments.forEach(comment => {
            container.appendChild(this.renderComment(comment));
        });
    }
}
