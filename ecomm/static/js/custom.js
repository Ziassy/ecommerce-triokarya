const ratingInputs = document.querySelectorAll('.rating input[type="radio"]');
const stars = document.querySelectorAll('.rating label i');

stars.forEach((star, index) => {
  star.addEventListener('click', () => {
    ratingInputs[index].checked = true;
    // Mengatur warna bintang berdasarkan yang dipilih
    for (let i = 0; i < stars.length; i++) {
      if (i <= index) {
        stars[i].style.color = '#ffc107';
      } else {
        stars[i].style.color = '#ccc';
      }
    }
  });
});


