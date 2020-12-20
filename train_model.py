from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import argparse
import pickle
import sys
import os

def entrenar_sistema():
	try:
		# load the face embeddings
		data = pickle.loads(open("output/embeddings.pickle", "rb").read())

		# encode the labels
		le = LabelEncoder()
		labels = le.fit_transform(data["names"])

		# train the model used to accept the 128-d embeddings of the face and
		# then produce the actual face recognition
		recognizer = SVC(C=1.0, kernel="linear", probability=True)
		recognizer.fit(data["embeddings"], labels)

		# write the actual face recognition model to disk
		#os.remove("output/recognizer.pickle")
		f = open("output/recognizer.pickle", "wb")
		f.write(pickle.dumps(recognizer))
		f.close()

		# write the label encoder to disk
		#os.remove("output/le.pickle")
		f = open("output/le.pickle", "wb")
		f.write(pickle.dumps(le))
		f.close()

		return "Aprendizaje realizado correctamente."
	except:
		return "Error de aprendizaje.", sys.exc_info()[0], ". No olvide que debe de tener minimo dos personas para poder usar el aprendizaje."


if __name__ == '__main__':
    entrenar_sistema()

