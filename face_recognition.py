import glob
import os
import cv2
from tqdm import tqdm

COSINE_THRESHOLD = 0.5
directory = 'data'
weights = os.path.join(directory, "models", "face_detection_yunet_2023mar.onnx")
face_detector = cv2.FaceDetectorYN.create(weights, "", (0, 0))
face_detector.setScoreThreshold(0.87)

weights = os.path.join(directory, "models", "face_recognition_sface_2021dec.onnx")
face_recognizer = cv2.FaceRecognizerSF.create(weights, "")


class FaceRecognition:
    def __init__(self, directory: str = 'data'):
        self._directory = directory
        self.dictionary = self._load_photo()

    def match(self, feature1):
        max_score = 0.0
        sim_user_id = ""
        for user_id, feature2 in zip(self.dictionary.keys(), self.dictionary.values()):
            score = face_recognizer.match(feature1, feature2, cv2.FaceRecognizerSF_FR_COSINE)
            if score >= max_score:
                max_score = score
                sim_user_id = user_id
        if max_score < COSINE_THRESHOLD:
            return False, ("", 0.0)
        return True, (sim_user_id, max_score)

    def recognize_face(self, image, file_name=None):
        channels = 1 if len(image.shape) == 2 else image.shape[2]
        if channels == 1:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
        if channels == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

        if image.shape[0] > 1000:
            image = cv2.resize(image, (0, 0), fx=500 / image.shape[0], fy=500 / image.shape[0])

        height, width, _ = image.shape
        face_detector.setInputSize((width, height))
        try:
            _, faces = face_detector.detect(image)
            if file_name is not None:
                assert len(faces) > 0, f'the file {file_name} has no face'

            faces = faces if faces is not None else []
            features = []
            for face in faces:
                aligned_face = face_recognizer.alignCrop(image, face)
                feat = face_recognizer.feature(aligned_face)

                features.append(feat)
            return features, faces
        except Exception as e:
            print(e)
            print(file_name)
            return None, None

    def _load_photo(self):
        # Get registered photos and return as npy files
        # File name = id name, embeddings of a photo is the representative for the id
        # If many files have the same name, an average embedding is used
        dictionary = {}
        # the tuple of file types, please ADD MORE if you want
        types = ('*.jpg', '*.png', '*.jpeg', '*.JPG', '*.PNG', '*.JPEG')
        files = []
        for a_type in types:
            files.extend(glob.glob(os.path.join(self._directory, 'images', a_type)))

        files = list(set(files))

        for file in tqdm(files):
            image = cv2.imread(file)
            feats, faces = self.recognize_face(image, file)
            if faces is None:
                continue
            user_id = os.path.splitext(os.path.basename(file))[0]
            dictionary[user_id] = feats[0]
        print(f'there are {len(dictionary)} ids')
        return dictionary
