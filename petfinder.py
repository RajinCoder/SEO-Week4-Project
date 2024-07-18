import requests

api_key = 'hg4nsv85lppeoqqixy3tnlt3k8lj6o0c'
base_url = "https://api-staging.adoptapet.com/search/"

payload={}
headers = {
  'Accept': 'application/json',
}

hypo_breeds = ['siberian', 'balinese', 'oriental shorthair', 'russian blue', 'devon rex',
                'poodle', 'bichon frise', 'portuguese water dog', 'maltese', 'schnauzer',
                  'rex rabbit', 'angora rabbit', 'mini rex']


"""
 Returns a list of pets(dogs,cats,rabbits,bird) posts from the user's input requests 
"""
def api_query_response(species, city_or_zip, geo_range, sex, age, special_needs, size, allergies):
    url = f'{base_url}pet_search?key={api_key}&v=3&output=json'
    resulting_pets = []
    params = {
        'species': f'{species}',
        'city_or_zip': f'{city_or_zip}',
        'geo_range': f'{geo_range}',
        'sex': f'{sex}',
        'age': f'{age}',
        'special_needs': f'{special_needs}',
        'pet_size_range_id': f'{size}'
    }

    response = requests.request("GET", url, headers=headers, data=payload, params=params)

    try:
        list_of_pet_dictionaries = response.json()["pets"]
    except KeyError:
        print("Try different query")
    else:
        for dictionary in list_of_pet_dictionaries:
            resulting_pets_dictionary = {}
            if not allergies or dictionary.get('primary_breed').lower() in hypo_breeds:
                resulting_pets_dictionary['pet_id'] = dictionary.get('pet_id')
                resulting_pets_dictionary['pet_name'] = dictionary.get('pet_name')
                resulting_pets_dictionary['primary_breed'] = dictionary.get('primary_breed')
                resulting_pets_dictionary['secondary_breed'] = dictionary.get('secondary_breed')
                resulting_pets_dictionary['sex'] = dictionary.get('sex')
                resulting_pets_dictionary['age'] = dictionary.get('age')
                resulting_pets_dictionary['size'] = dictionary.get('size')
                resulting_pets_dictionary['photo_link'] = dictionary.get('results_photo_url')
                resulting_pets.append(resulting_pets_dictionary)
    finally:
        return resulting_pets

#print(api_query_response('rabbit', '32703', '100', '', 'young', '0', '', False))

"""
 Returns data about a specific dog by their pet_id
"""      
def chosen_post_data(pet_id):
  url = f'{base_url}limited_pet_details?key={api_key}&v=3&output=json'
  params = {'pet_id': pet_id}

  response = requests.request("GET", url, headers=headers, data=payload, params=params)
  try:
    chosen_pet_dictionary = response.json()['pet']
  except KeyError:
    print("No pets by that ID")
  else:
    return chosen_pet_dictionary
