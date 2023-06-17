import boto3

# Create a Rekognition client
client = boto3.client(
    'rekognition',
    region_name='eu-west-1',  # update to your region
    aws_access_key_id='AKIAW6NNRBIWIGN3BIVM',
    aws_secret_access_key='DYn15gIJwC6jDj52Rpe6wKNM7TuhDpVN9euZ/BCC',
)

# Specify the image as bytes
with open('media/test_image.jpg', 'rb') as image:
    image_bytes = image.read()

# Perform facial analysis
response = client.detect_faces(
    Image={'Bytes': image_bytes},
    Attributes=['ALL']
)
from collections import OrderedDict

# Get face details from the response
face_details = response['FaceDetails']

# Define a list of attributes to keep
attributes_to_keep = ["AgeRange", "Smile", "Gender", "Emotions"]

# Prepare dictionary for face attributes
face_attributes = {}

# Emotion to RGB color mapping
emotion_colors = {
    'ANGRY': (255, 0, 0),
    'HAPPY': (255, 255, 0),
    'SAD': (0, 0, 0),
    'CONFUSED': (0, 0, 255),
    'DISGUSTED': (255, 0, 125),
    'SURPRISED': (255, 125, 0),
    'CALM': (0, 255, 0),
    'FEAR': (125, 0, 255)
}

# Extract attributes of each face
for i, face in enumerate(face_details):
    face_dict = OrderedDict()
    for attribute, value in face.items():
        if attribute in attributes_to_keep:
            if attribute == 'AgeRange':
                face_dict['Age_Median'] = (value['Low'] + value['High']) / 2
                face_dict['Age_Range'] = value['High'] - value['Low']
            elif attribute == 'Smile':
                if value['Value']:  # if Smile is True
                    face_dict[attribute] = round(value['Confidence'])/10 # /10to fit painting scale
                else:  # if Smile is False
                    face_dict[attribute] = round(100 - value['Confidence']) /10 # /10to fit painting scale
                # print(f"Smile value: {value['Value']}, Confidence: {value['Confidence']}")
            elif attribute == 'Gender':
                if value['Value'] == 'Female': #scale = female = 0, average =5
                    face_dict[attribute] = round((1-(value['Confidence']/100) )*10 , 2)
                elif value['Value'] == 'Male': #scale = male = 10, average =5
                    face_dict[attribute] = round((value['Confidence'] /100 ) * 10, 2)
            elif attribute == 'Emotions':
                # sort the emotions by confidence and get the two most confident
                most_confident_emotions = sorted(value, key=lambda x:x['Confidence'], reverse=True)[:2]
                colors = [emotion_colors[emotion['Type']] for emotion in most_confident_emotions]
                # Average the RGB values of the two most confident emotions
                average_color = tuple(sum(x)/len(x) for x in zip(*colors))
                face_dict['Average_Color'] = average_color

    # Reorder the dictionary as per your preference
    ordered_face_dict = OrderedDict([
        ('Age_Median', face_dict.get('Age_Median')),
        ('Smile', face_dict.get('Smile')),
        ('Gender', face_dict.get('Gender')),
        ('Age_Range', face_dict.get('Age_Range')),
        ('Average_Color', face_dict.get('Average_Color')),
    ])

    face_attributes[f'Face_{i+1}'] = ordered_face_dict


# Now face_attributes dictionary contains the required details of each face
print(face_attributes)
