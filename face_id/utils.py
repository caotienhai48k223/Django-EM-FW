import face_recognition as fr
import numpy as np
from .models import Profile


def is_ajax(request):
  return request.headers.get('x-requested-with') == 'XMLHttpRequest'



def classify_face(img, username=None):
  if username:
    profiles = Profile.objects.filter(user__username=username)
  else:
    profiles  = Profile.objects.exclude(photo='')
  encoded = {}
  for profile in profiles:
    face = fr.load_image_file(profile.photo.path)
    face_encodings = fr.face_encodings(face)
    if face_encodings:
      encoded[profile.user.username] = face_encodings[0]
    else:
      print('No face found in the image')  
  
  faces_encoded = list(encoded.values())
  known_face_names = list(encoded.keys())
  
  img = fr.load_image_file(img)

  try:
    face_locations = fr.face_locations(img)
    unknown_face_encodings = fr.face_encodings(img, face_locations)
    face_names = []
    for face_encoding in unknown_face_encodings:
      matches = fr.compare_faces(faces_encoded, face_encoding)
      face_distances = fr.face_distance(faces_encoded, face_encoding)
      best_match_index = np.argmin(face_distances)
      
      if matches[best_match_index]:
        name = known_face_names[best_match_index]
      else:
        name = 'Chịu Đó'
      face_names.append(name)
    return face_names[0]
  except Exception as e:
    print(f"Error in classify_face: {e}")
    return False



  
  
  
  

