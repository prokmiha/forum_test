export const Validation = {
    username(value) {
        if (!value || value.trim().length < 3) {
            throw new Error("Имя должно содержать минимум 3 символа");
        }
        const pattern = /^[A-Za-zА-Яа-я0-9 ]+$/;
        if (!pattern.test(value)) {
            throw new Error("Имя может содержать только латиницу, кириллицу и цифры");
        }
        return true;
    },

    email(value) {
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!pattern.test(value)) {
            throw new Error("Некорректный формат email");
        }
        return true;
    },
}; 