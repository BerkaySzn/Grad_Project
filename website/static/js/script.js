// JavaScript for Recipe Finder

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Image preview for file upload
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function() {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // If you want to show a preview of the image
                    // You can add an img element with id="preview" to your HTML
                    const preview = document.getElementById('preview');
                    if (preview) {
                        preview.src = e.target.result;
                        preview.style.display = 'block';
                    }
                }
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}); 
document.addEventListener('DOMContentLoaded', function() {
    // Modelin getirdiği ingredient'leri düzgün şekilde listeye ekle
    fetch('/get-ingredients')
    .then(response => response.json())
    .then(data => {
        console.log("Modelden Gelen Ingredients:", data);  // Konsolda kontrol için

        // Listeyi temizle ve güncelle
        const ingredientList = document.getElementById('ingredient-list');
        ingredientList.innerHTML = '';

        data.ingredients.forEach(ingredient => {
            const ingredientItem = document.createElement('div');
            ingredientItem.className = 'ingredient-item p-3 mb-2 bg-light rounded';
            
            // Eğer ingredient nesne formatındaysa name al, değilse direkt yaz
            if (typeof ingredient === 'object' && ingredient.name) {
                ingredientItem.textContent = ingredient.name;
            } else {
                ingredientItem.textContent = ingredient;
            }
            
            ingredientList.appendChild(ingredientItem);
        });

        console.log("Updated Ingredient List:", ingredientList.innerHTML);
    })
    .catch(error => console.error('Error fetching ingredients:', error));
});
