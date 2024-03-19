import time

import cv2
from face_recognition import FaceRecognition
from user_manager import UserManager
from RGB_light import RGBLight


def stream(source: int | str = 0):
    previous = ''
    previous_recognized = []
    user_manager = UserManager()
    light = RGBLight()
    fr = FaceRecognition()
    capture = cv2.VideoCapture(source)
    if not capture.isOpened():
        return

    cTime , pTime = 0, 0
    while True:
        recognized = []
        result, image = capture.read()
        if result is False:
            cv2.waitKey(0)
            break

        features, faces = fr.recognize_face(image)
        if faces is None:
            continue

        for idx, (face, feature) in enumerate(zip(faces, features)):
            result, user = fr.match(feature)
            box = list(map(int, face[:4]))
            color = (0, 255, 0) if result else (0, 0, 255)
            thickness = 2
            cv2.rectangle(image, box, color, thickness, cv2.LINE_AA)

            id_name, score = user if result else (f"unknown_{idx}", 0.0)
            if id_name.split('_')[0] != 'unknown' and id_name not in recognized:
                recognized.append(id_name)

            text = "{0} ({1:.2f})".format(id_name, score)
            position = (box[0], box[1] - 10)
            font = cv2.FONT_HERSHEY_SIMPLEX
            scale = 0.6
            cv2.putText(image, text, position, font, scale, color, thickness, cv2.LINE_AA)

        # print(len(recognized))
        if len(recognized) > 0:
            recognized.sort()
            # print(str(recognized) + " " + str(previous_recognized))
            if previous_recognized != recognized:
                previous_recognized = recognized

            if previous != previous_recognized[0]:
                previous = recognized[0]
                print('Riconosciuto/a: ' + previous)
                light.change_color(user_manager.get_user_color(recognized[0]))

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(image, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 255), 3)

        cv2.imshow("face recognition", image)
        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    ipcam = 'rtsp://admin:admin@192.168.4.110:554//cam/realmonitor?channel=1&subtype=1&unicast=true'
    while True:
        i = input('1 - inizia la stream\n2 - aggiungi un utente\n0 - Esci\n')
        i = int(i)
        if i == 1:
            stream(ipcam)
        elif i == 2:
            user = UserManager(video_source=ipcam)
            user.add_user()
        elif i == 0:
            exit()
