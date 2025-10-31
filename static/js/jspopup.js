document.addEventListener("DOMContentLoaded", function () {
  // Ambil semua item produk
  const itemProduk = document.querySelectorAll(".item-produk");
  const modalElement = document.getElementById("popupDeskripsi");
  const modal = new bootstrap.Modal(modalElement);
  let hoverTimeout;

  // Tambahkan event listener untuk setiap item
  itemProduk.forEach((item) => {
    // Event untuk hover (desktop)
    item.addEventListener("mouseenter", function () {
      const nama = this.getAttribute("data-nama");
      const deskripsi = this.getAttribute("data-deskripsi");

      // Delay sebelum popup muncul
      hoverTimeout = setTimeout(() => {
        document.getElementById("modalNamaProduk").textContent = nama;
        document.getElementById("modalDeskripsiProduk").textContent = deskripsi;
        modal.show();
      }, 300); // Popup muncul setelah 0.3 detik hover
    });

    // Tutup popup saat mouse keluar dari item
    item.addEventListener("mouseleave", function () {
      clearTimeout(hoverTimeout);
      modal.hide();
    });

    // Event untuk touch (mobile)
    item.addEventListener("touchstart", function (e) {
      const nama = this.getAttribute("data-nama");
      const deskripsi = this.getAttribute("data-deskripsi");

      document.getElementById("modalNamaProduk").textContent = nama;
      document.getElementById("modalDeskripsiProduk").textContent = deskripsi;
      modal.show();
    });
  });

  // Tutup popup saat klik di luar modal
  modalElement.addEventListener("click", function (e) {
    if (e.target === modalElement) {
      modal.hide();
    }
  });
});
