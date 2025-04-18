function openModal(button) {
    const detailText = button.getAttribute("data-details");
    if (!detailText) return;  // Don't open if there's no text

    document.getElementById("detailModal").style.display = "block";
}

function closeModal() {
    document.getElementById("detailModal").style.display = "none";
}
