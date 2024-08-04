document.addEventListener('DOMContentLoaded', function () {
  const provinsiSelect = document.getElementById('provinsi');
  const kabupatenSelect = document.getElementById('kabupaten');
  const kecamatanSelect = document.getElementById('kecamatan');
  const kelurahanSelect = document.getElementById('kelurahan');

  provinsiSelect.addEventListener('change', function () {
    const provinsiId = this.value;
    fetch(`/get-kabupaten/?provinsi_id=${provinsiId}`)
      .then(response => response.json())
      .then(data => {
        kabupatenSelect.innerHTML = '<option value="" selected disabled>Select Kabupaten</option>';
        kecamatanSelect.innerHTML = '<option value="" selected disabled>Select Kecamatan</option>';
        kelurahanSelect.innerHTML = '<option value="" selected disabled>Select Kelurahan</option>';
        data.forEach(kabupaten => {
          const option = document.createElement('option');
          option.value = kabupaten.id;
          option.textContent = kabupaten.name;
          kabupatenSelect.appendChild(option);
        });
      });
  });

  kabupatenSelect.addEventListener('change', function () {
    const kabupatenId = this.value;
    fetch(`/get-kecamatan/?kabupaten_id=${kabupatenId}`)
      .then(response => response.json())
      .then(data => {
        kecamatanSelect.innerHTML = '<option value="" selected disabled>Select Kecamatan</option>';
        kelurahanSelect.innerHTML = '<option value="" selected disabled>Select Kelurahan</option>';
        data.forEach(kecamatan => {
          const option = document.createElement('option');
          option.value = kecamatan.id;
          option.textContent = kecamatan.name;
          kecamatanSelect.appendChild(option);
        });
      });
  });

  kecamatanSelect.addEventListener('change', function () {
    const kecamatanId = this.value;
    fetch(`/get-kelurahan/?kecamatan_id=${kecamatanId}`)
      .then(response => response.json())
      .then(data => {
        kelurahanSelect.innerHTML = '<option value="" selected disabled>Select Kelurahan</option>';
        data.forEach(kelurahan => {
          const option = document.createElement('option');
          option.value = kelurahan.id;
          option.textContent = kelurahan.name;
          kelurahanSelect.appendChild(option);
        });
      });
  });
});