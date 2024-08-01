document.addEventListener('DOMContentLoaded', () => {

  const toggleShippingCosts = (radio) => {
    const shippingCostsSection = document.getElementById('shipping-costs-section');
    const codPaymentOption = document.getElementById('C');
    // Memeriksa nilai dari elemen radio yang dipilih
    if (radio.value === 'EX') {
      shippingCostsSection.style.display = 'block';
      // Menyembunyikan opsi pembayaran COD
      if (codPaymentOption) {
        codPaymentOption.closest('.form-check').style.display = 'none';
      }
    } else {
      shippingCostsSection.style.display = 'none';
      // Menampilkan opsi pembayaran COD
      if (codPaymentOption) {
        codPaymentOption.closest('.form-check').style.display = 'block';
      }
    }
  };

  // Menambahkan event listener pada semua tombol radio opsi pengiriman
  const shippingOptions = document.querySelectorAll('input[name="opsi_pengiriman"]');
  shippingOptions.forEach(option => {
    option.addEventListener('change', (event) => toggleShippingCosts(event.target));
  });

  // Panggilan awal untuk mengatur visibilitas yang benar saat halaman dimuat
  const selectedOption = document.querySelector('input[name="opsi_pengiriman"]:checked');
  if (selectedOption) {
    toggleShippingCosts(selectedOption);
  } else {
    document.getElementById('shipping-costs-section').style.display = 'none';
  }
});
