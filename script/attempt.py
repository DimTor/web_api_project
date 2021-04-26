from sklearn.cluster import KMeans
from script import utils
import cv2


def make_bar(image, clusters):
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	image = image.reshape((image.shape[0] * image.shape[1], 3))
	clt = KMeans(n_clusters=clusters)
	clt.fit(image)

	hist = utils.centroid_histogram(clt)
	bar = utils.plot_colors(hist, clt.cluster_centers_)
	# show our color bart
	return bar
