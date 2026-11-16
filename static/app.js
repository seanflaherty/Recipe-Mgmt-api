let currentRecipe = null;
let editingRecipeId = null;

// Show message function
let messageTimeout = null;

function showMessage(text, isError = false) {
    const resultDiv = document.getElementById('result-message');
    if (!resultDiv) return;

    // Clear any existing auto-dismiss timer so messages don't cut each other off
    if (messageTimeout) {
        clearTimeout(messageTimeout);
        messageTimeout = null;
    }

    const styles = isError
        ? 'bg-red-50 text-red-700 border-red-200'
        : 'bg-emerald-50 text-emerald-700 border-emerald-200';

    resultDiv.innerHTML = `
        <div class="p-3 ${styles} rounded-lg border text-xs flex justify-between items-center gap-2">
            <span>${text}</span>
            <button type="button" onclick="clearMessage()"
                class="font-bold text-base leading-none opacity-60 hover:opacity-100 transition"
                aria-label="Dismiss message">&times;</button>
        </div>
    `;

    // Auto-dismiss success notices after 4 seconds; leave errors up until dismissed
    if (!isError) {
        messageTimeout = setTimeout(clearMessage, 4000);
    }
}

function clearMessage() {
    const resultDiv = document.getElementById('result-message');
    if (resultDiv) resultDiv.innerHTML = '';
}

// Edit recipe function
function startEditRecipe() {
    if (!currentRecipe) return;

    editingRecipeId = currentRecipe.id;

    // Update form heading & buttons for Edit Mode
    document.getElementById('form-title').innerText = `Edit Recipe: ${currentRecipe.name}`;
    document.getElementById('submit-btn').innerText = 'Update Recipe';
    document.getElementById('cancel-edit-btn').classList.remove('hidden');

    // Populate recipe name
    document.getElementById('recipe-name').value = currentRecipe.name;

    // Populate ingredient rows (reusing your existing addIngredient helper!)
    const ingContainer = document.getElementById('ingredients-container');
    ingContainer.innerHTML = '';
    if (currentRecipe.ingredients && currentRecipe.ingredients.length > 0) {
        currentRecipe.ingredients.forEach(ing => {
            const tagsStr = ing.dietary_tags ? ing.dietary_tags.join(', ') : '';
            addIngredient(ing.name, tagsStr, ing.quantity, ing.unit);
        });
    } else {
        addIngredient();
    }

    // Populate instruction rows (reusing your existing addInstructionStep helper!)
    const insContainer = document.getElementById('instructions-container');
    insContainer.innerHTML = '';
    if (currentRecipe.instructions && currentRecipe.instructions.length > 0) {
        currentRecipe.instructions.forEach(ins => {
            const equipStr = ins.equipment ? ins.equipment.join(', ') : '';
            addInstructionStep(ins.description, equipStr, ins.prep_time, ins.include_in_prep_time);
        });
    } else {
        addInstructionStep();
    }

    // Close modal and scroll smoothly to the form
    closeRecipeModal();
    document.getElementById('recipe-form').scrollIntoView({ behavior: 'smooth' });
}

function cancelEdit() {
    editingRecipeId = null;
    document.getElementById('form-title').innerText = 'Add a New Recipe';
    document.getElementById('submit-btn').innerText = 'Save Recipe to Database';
    document.getElementById('cancel-edit-btn').classList.add('hidden');

    document.getElementById('recipe-form').reset();
    document.getElementById('ingredients-container').innerHTML = '';
    addIngredient();
    document.getElementById('instructions-container').innerHTML = '';
    addInstructionStep();
}


// Helper function to append a new ingredient row
function addIngredient(ingredientName = '', dietaryTags = '', quantity = 1, unit = '') {
    const container = document.getElementById('ingredients-container');
    const row = document.createElement('div');
    row.className = 'ingredient-row p-3 bg-gray-50 rounded-lg border border-gray-200 space-y-2';
    row.innerHTML = `
    <div>
        <label class="block text-xs font-medium text-gray-500 mb-1">Ingredient Name</label>
        <input type="text" placeholder="e.g. Flour" value="${ingredientName}" required
            class="ing-name w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
    </div>
    <div>
        <label class="block text-xs font-medium text-gray-500 mb-1">Dietary Tags (comma-separated)</label>
        <input type="text" placeholder="e.g. VEGAN, GLUTEN" value="${dietaryTags}"
            class="ing-tags w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
    </div>
    <div class="grid grid-cols-2 gap-2">
        <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Quantity</label>
            <input type="number" step="0.1" value="${quantity}" required
                class="ing-quantity w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
        </div>
        <div>
            <label class="block text-xs font-medium text-gray-500 mb-1">Unit</label>
            <input type="text" placeholder="e.g. cups" value="${unit}" required
                class="ing-unit w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
        </div>
    </div>
    <div class="flex items-center justify-between pt-1">
        <button type="button" onclick="this.closest('.ingredient-row').remove()"
            class="text-xs text-red-500 hover:text-red-700 font-medium">
            Remove Ingredient
        </button>
    </div>
    `;
    container.appendChild(row);
}

// Helper function to append a new step row
function addInstructionStep(instruction = '', equipment = '', prepTime = 5, includeInPrep = true) {
    const container = document.getElementById('instructions-container');
    const row = document.createElement('div');
    row.className = 'instruction-row p-3 bg-gray-50 rounded-lg border border-gray-200 space-y-2';
    row.innerHTML = `
    <div>
        <label class="block text-xs font-medium text-gray-500 mb-1">Instruction</label>
        <input type="text" placeholder="e.g. Mix ingredients in a bowl." value="${instruction}" required
            class="ins-desc w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
    </div>
    <div>
        <label class="block text-xs font-medium text-gray-500 mb-1">Equipment</label>
        <input type="text" placeholder="e.g. mixing bowl, spoon" value="${equipment}"
            class="ins-equip w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
    </div>
    <div>
        <label class="block text-xs font-medium text-gray-500 mb-1">Step Prep Time (minutes)</label>
        <input type="number" value="${prepTime}" required
            class="ins-time w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white">
    </div>
    <div class="flex items-center justify-between pt-1">
        <label class="flex items-center space-x-2 text-xs font-medium text-gray-600">
            <input type="checkbox" ${includeInPrep ? 'checked' : ''} class="ins-include w-4 h-4 text-emerald-600 border-gray-300 rounded focus:ring-emerald-500">
                <span>Include in total prep time?</span>
        </label>
        <button type="button" onclick="this.closest('.instruction-row').remove()"
            class="text-xs text-red-500 hover:text-red-700 font-medium">
            Remove Step
        </button>
    </div>
    `;
    container.appendChild(row);
}

async function submitRecipe(event) {
    event.preventDefault();

    const name = document.getElementById('recipe-name').value;

    // Collect all ingredient rows dynamically
    const ingredientRows = document.querySelectorAll('.ingredient-row');
    const recipeIngredients = [];
    ingredientRows.forEach(row => {
        const ingredientName = row.querySelector('.ing-name').value;
        const dietaryTagsRaw = row.querySelector('.ing-tags').value;
        const dietaryTags = dietaryTagsRaw ? dietaryTagsRaw.split(',').map(e => e.trim()).filter(e => e.length > 0) : [];
        const quantity = parseFloat(row.querySelector('.ing-quantity').value);
        const unit = row.querySelector('.ing-unit').value;

        recipeIngredients.push({
            ingredient: {
                name: ingredientName,
                dietary_tags: dietaryTags
            },
            quantity: quantity,
            unit: unit
        });
    });

    // Collect all instruction rows dynamically
    const instructionRows = document.querySelectorAll('.instruction-row');
    const instructions = [];
    instructionRows.forEach(row => {
        const desc = row.querySelector('.ins-desc').value;
        const equipRaw = row.querySelector('.ins-equip').value;
        const equipment = equipRaw ? equipRaw.split(',').map(e => e.trim()).filter(e => e.length > 0) : [];
        const prepTime = parseInt(row.querySelector('.ins-time').value, 10);
        const includeInPrepTime = row.querySelector('.ins-include').checked;

        instructions.push({
            description: desc,
            prep_time: prepTime,
            equipment: equipment,
            include_in_prep_time: includeInPrepTime
        });
    });

    const payload = {
        name: name,
        recipe_ingredients: recipeIngredients,
        instructions: instructions
    };

    const url = editingRecipeId ? `/recipes/${editingRecipeId}` : '/recipes';
    const method = editingRecipeId ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        const resultDiv = document.getElementById('result-message');

        if (response.ok) {
            showMessage(result.message);
            loadRecipes();
            cancelEdit();
        } else {
            showMessage(`Error: ${result.detail || 'Failed to save'}`, true);
        }
    } catch (err) {
        showMessage(`Network error: ${err.message}`, true);
    }
}

// Functions to open and populate the modal with recipe details
function openRecipeModal(button) {
    const modal = document.getElementById('recipe-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');

    const recipeData = JSON.parse(button.getAttribute('data-recipe'));
    currentRecipe = recipeData;  // <-- Store the active recipe
    modalTitle.innerText = recipeData.name;

    let ingredientsHtml = '<h4 class="font-semibold text-gray-700 mt-2">Ingredients:</h4><ul class="list-disc list-inside space-y-1 text-sm">';
    if (recipeData.ingredients && recipeData.ingredients.length > 0) {
        recipeData.ingredients.forEach(ing => {
            const tags = ing.dietary_tags && ing.dietary_tags.length > 0 ? ` <span class="text-xs bg-emerald-50 text-emerald-600 px-1.5 py-0.5 rounded">${ing.dietary_tags.join(', ')}</span>` : '';
            ingredientsHtml += `<li>${ing.quantity} ${ing.unit} ${ing.name}${tags}</li>`;
        });
    } else {
        ingredientsHtml += '<li class="text-gray-400 italic">No ingredients listed.</li>';
    }
    ingredientsHtml += '</ul>';

    let instructionsHtml = '<h4 class="font-semibold text-gray-700 mt-4">Instructions:</h4><ol class="list-decimal list-inside space-y-2 text-sm">';
    if (recipeData.instructions && recipeData.instructions.length > 0) {
        recipeData.instructions.forEach(ins => {
            const equipText = ins.equipment && ins.equipment.length > 0
                ? ` <span class="text-xs text-gray-500 font-medium">[Equipment: ${ins.equipment.join(', ')}]</span>`
                : '';
            const prepNote = ins.include_in_prep_time
                ? `(Prep: ${ins.prep_time} mins)`
                : `(Prep: ${ins.prep_time} mins - excluded)`;

            instructionsHtml += `<li>${ins.description}${equipText} <span class="text-xs text-gray-400">${prepNote}</span></li>`;
        });
    } else {
        instructionsHtml += '<li class="text-gray-400 italic">No instructions listed.</li>';
    }
    instructionsHtml += '</ol>';

    modalContent.innerHTML = `
    <p class="text-sm"><strong>Total Prep Time:</strong> ${recipeData.total_prep_time} minutes</p>
    ${ingredientsHtml}
    ${instructionsHtml}
    `;

    modal.classList.remove('hidden');
}

async function deleteRecipe() {
    if (!currentRecipe || !currentRecipe.id) {
        alert("Error: Recipe ID not found.");
        return;
    }

    // Confirm before permanently deleting
    const confirmed = confirm(`Are you sure you want to delete "${currentRecipe.name}"?`);
    if (!confirmed) return;

    try {
        const response = await fetch(`/recipes/${currentRecipe.id}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            closeRecipeModal();
            loadRecipes(); // Refresh the Recipe Book list on the right

            const resultDiv = document.getElementById('result-message');
            if (resultDiv) {
                resultDiv.innerHTML = `<div class='p-3 bg-emerald-50 text-emerald-700 rounded-lg border border-emerald-200 text-xs'>Deleted "${currentRecipe.name}".</div>`;
            }
        } else {
            const errorData = await response.json().catch(() => ({}));
            showMessage(`Failed to delete recipe: ${errorData.detail || response.statusText}`, true);
        }
    } catch (err) {
        showMessage(`Network error: ${err.message}`, true);
    }
}

function closeRecipeModal() {
    document.getElementById('recipe-modal').classList.add('hidden');
}

async function loadRecipes() {
    const container = document.getElementById('recipe-list-container');
    container.innerHTML = "<p class='text-gray-400 italic text-sm'>Loading recipes from database...</p>";

    const url = editingRecipeId ? `/recipes/${editingRecipeId}` : '/recipes';
    const method = editingRecipeId ? 'PUT' : 'POST';

    try {
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        const resultDiv = document.getElementById('result-message');

        if (response.ok) {
            closeRecipeModal();
            loadRecipes();
            showMessage(`Deleted "${currentRecipe.name}".`);
        }
    } catch (err) {
        document.getElementById('result-message').innerHTML = `<div class='p-3 bg-red-50 text-red-700 rounded-lg border border-red-200 text-xs'>Network error: ${err.message}</div>`;
    }
}

async function loadRecipes() {
    const container = document.getElementById('recipe-list-container');
    container.innerHTML = "<p class='text-gray-400 italic text-sm'>Loading recipes from database...</p>";

    try {
        const response = await fetch('/recipes-db');
        const htmlContent = await response.text();
        container.innerHTML = htmlContent;
    } catch (err) {
        container.innerHTML = `<p class='text-red-500 text-xs'>Failed to load recipes: ${err.message}</p>`;
    }
}

window.addEventListener('DOMContentLoaded', loadRecipes);
