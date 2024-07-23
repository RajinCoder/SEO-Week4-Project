
const ageMapping = {
    "any": "",
    "young": "young",
    "adult": "adult",
    "senior": "senior",
    "puppy": "puppy"
};

const specialNeedsMapping = {
    "yes": 1,
    "no": 0
}

const sexMapping = {
    "any": "",
    "male": "m",
    "m": "m",
    "female": "f",
    "f": "f"
};

const petSizeRangeMapping = {
    "any": "",
    "small": 1,
    "medium": 2,
    "large": 3,
    "x-large": 4
};

const allergiesMap = {
    "yes": true,
    "no": false
}

const validateInput = (input, mapping) => {
    return mapping[input.toLowerCase()] !== undefined ? mapping[input.toLowerCase()] : null;
};

document.getElementById('inputForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const location = document.getElementById('question1').value;
    const geoRange = document.getElementById('question2').value;
    const special = validateInput(document.getElementById('question3').value, specialNeedsMapping);
    const sex = validateInput(document.getElementById('question4').value, sexMapping);
    const housing = document.getElementById('question5').value;
    const allergies = document.getElementById('question6').value;
    const activity_level = document.getElementById('question7').value;
    const attention = document.getElementById('question8').value;

    const species = figureSpecies(housing, activity_level, attention, allergies);
    const size = validateInput(figureSize(housing), petSizeRangeMapping);
    const age = figureAge(attention, species);
    console.log('Species:', species);
    console.log('Size:', size);
    console.log('Age:', age);

    if (age === null || sex === null || special === null || size === null || isNaN(geoRange) || geoRange <= 0 || species === null) {
        alert('Invalid input values. Please check your answers.');
        return;
    }

    let formData = {
        species: species,
        age: age,
        size: size,
        sex: sex,
        geo_range: geoRange,
        location: location,
        special_ability: special,
        allergies: validateInput(allergies, allergiesMap) 
    };

    console.log(formData);

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        } else {
            console.error('Error:', data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
});

const getRandomElement = (array) => {
    const randomIndex = Math.floor(Math.random() * array.length);
    return array[randomIndex];
};

/**
 * Determines the size of the pet based on potential housing.
 * @param {*} housing the housing condition of the pet
 * @returns a recommended size for the pet
 */
const figureSize = (housing) => {
    if (housing.toLowerCase() === 'apartment') {
        return "small"; // Prefer smaller pets for apartments
    } else if (housing.toLowerCase() === 'house') {
        return "any";
    } else {
        return null; // Invalid housing input
    }
};



/**
 * Determines recommended age for pet based on desired attention requirements.
 * @param {*} attention the level of attention required
 * @param {*} species the species of the animal
 * @returns a string representing the age of the pet
 */
const figureAge = (attention, species) => {
    if (attention.toLowerCase() == 'low') {
        return getRandomElement(['adult', 'senior']);
    } else if (attention.toLowerCase() == 'high') {
        if (species.toLowerCase() == 'dog') {
            return "puppy";
        } else if (species.toLowerCase() == 'cat') {
            return "kitten";
        } else {
            return "young";
        }
    } else if (attention.toLowerCase() == 'moderate') {
        return getRandomElement(['adult', 'young']);
    } else {
        return null; // Invalid attention input
    }
};


/**
 * Determines recommended species based on variety of parameters.
 * @param {*} housing the housing condition for the pet
 * @param {*} activity_level the desired activity level of the pet
 * @param {*} attention the desired level of attention required
 * @param {*} allergies the boolean value of if the owner has allergies
 * @returns a string representing the recommended species of pet
 */
const figureSpecies = (housing, activity_level, attention, allergies) => {
    let speciesWeights = {
        dog: 0,
        cat: 0,
        bird: 0,
        rabbit: 0
    };

    if (!["apartment", "house"].includes(housing.toLowerCase())) {
        return null;
    }

    if (!["low", "moderate", "high"].includes(activity_level.toLowerCase())) {
        return null;
    }

    if (!["low", "moderate", "high"].includes(attention.toLowerCase())) {
        return null;
    }

    if (allergies.toLowerCase() === 'yes') {
        speciesWeights.bird = -Infinity; // Eliminate birds due to feathers
    }

    if (housing.toLowerCase() === 'apartment') {
        speciesWeights.dog -= 1; // Less favorable for large dogs
    }

    if (attention.toLowerCase() == 'low') {
        speciesWeights.cat += 1;
        speciesWeights.bird += 2; 
    } else if (attention.toLowerCase() == 'moderate'){
        speciesWeights.rabbit += 2;
        speciesWeights.cat += 2;
        speciesWeights.bird += 1; 
    } else if (attention.toLowerCase() == 'high') {
        speciesWeights.dog += 2; 
        speciesWeights.rabbit += 1.5;
        speciesWeights.bird += 1;
        speciesWeights.cat += 1.5;
    }

    if (activity_level.toLowerCase() === 'low') {
        speciesWeights.cat += 2;
        speciesWeights.bird += 2; 
    } else if (activity_level.toLowerCase() === 'moderate') {
        speciesWeights.rabbit += 2;
        speciesWeights.dog += 1;
        speciesWeights.cat += 1.5;
        speciesWeights.bird += 1; 
    } else if (activity_level.toLowerCase() === 'high'){
        speciesWeights.dog += 2;
        speciesWeights.rabbit += 1.5;
        speciesWeights.cat += 1;
        speciesWeights.bird += 1; 
    }

    return Object.keys(speciesWeights).reduce((a, b) => speciesWeights[a] > speciesWeights[b] ? a : b);
};

