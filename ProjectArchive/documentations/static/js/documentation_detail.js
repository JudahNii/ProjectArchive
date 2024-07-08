
document.querySelector("#open-popup").addEventListener("click", function () {
    document.body.classList.add("active-popup");
});

document.querySelector("#close-popup").addEventListener("click", function () {
    document.body.classList.remove("active-popup");
});


document.addEventListener('DOMContentLoaded', function () {
    const deleteBtn = document.querySelector('.delete-btn');
    if (deleteBtn) {
        deleteBtn.addEventListener('click', function (event) {
            event.preventDefault();
            const confirmation = confirm('Are you sure you want to delete this documentation?');
            if (confirmation) {
                this.closest('form').submit();
            }
        });
    }
});