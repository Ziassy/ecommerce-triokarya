document.addEventListener('DOMContentLoaded', () => {
  console.log('tes');

  const updateFinalTotal = () => {
    const shippingCostElement = document.getElementById('shipping-cost');
    const finalTotalElement = document.getElementById('final-total');
    const totalHargaElement = document.querySelector('.total-harga');

    const shippingCost = parseFloat(shippingCostElement.textContent.replace(/[^0-9.-]+/g, "")) || 0;
    const totalHarga = parseFloat(totalHargaElement.textContent.replace(/[^0-9.-]+/g, "")) || 0;
    const finalTotal = totalHarga + shippingCost;

    finalTotalElement.textContent = 'Rp ' + parseFloat(finalTotal.textContent.replace(/[^0-9.-]+/g, "")) || 0;
  };

  const toggleShippingCosts = (radio) => {
    const shippingCostsSection = document.getElementById('shipping-costs-section');
    const codPaymentOption = document.getElementById('C'); // ID untuk opsi COD

    // Mengatur visibilitas biaya pengiriman
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

  // Menambahkan event listener pada semua tombol radio opsi biaya pengiriman
  const shippingCostOptions = document.querySelectorAll('input[name="shipping_option"]');
  shippingCostOptions.forEach(option => {
    option.addEventListener('change', (event) => {
      const shippingCost = event.target.value;
      document.getElementById('shipping-cost').textContent = 'Rp ' + parseFloat(shippingCost).toLocaleString('id-ID', { minimumFractionDigits: 0 });
      updateFinalTotal();
    });
  });

  // Panggilan awal untuk mengatur visibilitas yang benar saat halaman dimuat
  const selectedOption = document.querySelector('input[name="opsi_pengiriman"]:checked');
  if (selectedOption) {
    toggleShippingCosts(selectedOption);
  } else {
    document.getElementById('shipping-costs-section').style.display = 'none';
  }

  // Perbarui total akhir saat halaman dimuat
  updateFinalTotal();
});
