import numpy as np
import cyvlfeat as vlfeat
from utils import *
import os.path as osp
from glob import glob
from random import shuffle
from IPython.core.debugger import set_trace
from sklearn.svm import LinearSVC
from time import time

# scales = [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3]
# scales = [1.0, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65]
# scales = [1.0, 0.9, 0.8, 0.7, 0.6]
scales = [0.8, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25]
# scales = [1.0, 0.7, 0.6]
# scales = [1.0]

# detection_scales = [1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4]
# detection_scales = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3]
detection_scales = [0.8, 0.7, 0.65, 0.6, 0.55, 0.5, 0.45, 0.4, 0.35, 0.3, 0.25]

return_all 			= False
step_size 			= 15
detect_step_size 	= 15
pos_ws				= 1.0

def get_positive_features(train_path_pos, feature_params):
	"""
	This function should return all positive training examples (faces) from
	36x36 images in 'train_path_pos'. Each face should be converted into a
	HoG template according to 'feature_params'.

	Useful functions:
	-   vlfeat.hog.hog(im, cell_size): computes HoG features

	Args:
	-   train_path_pos: (string) This directory contains 36x36 face images
	-   feature_params: dictionary of HoG feature computation parameters.
	    You can include various parameters in it. Two defaults are:
	        -   template_size: (default 36) The number of pixels spanned by
	        each train/test template.
	        -   hog_cell_size: (default 6) The number of pixels in each HoG
	        cell. template size should be evenly divisible by hog_cell_size.
	        Smaller HoG cell sizes tend to work better, but they make things
	        slower because the feature dimensionality increases and more
	        importantly the step size of the classifier decreases at test time
	        (although you don't have to make the detector step size equal a
	        single HoG cell).

	Returns:
	-   feats: N x D matrix where N is the number of faces and D is the template
	        dimensionality, which would be (feature_params['template_size'] /
	        feature_params['hog_cell_size'])^2 * 31 if you're using the default
	        hog parameters.
	"""
	# params for HOG computation
	win_size = feature_params.get('template_size', 36)
	cell_size = feature_params.get('hog_cell_size', 6)

	positive_files = glob(osp.join(train_path_pos, '*.jpg'))
	print("Number of face crops:",len(positive_files))

	###########################################################################
	#                           TODO: YOUR CODE HERE                          #
	###########################################################################

	#---------------- Starter code --------------------------------------------
	# n_cell = np.ceil(win_size/cell_size).astype('int') # n_cell = 6
	# feats = np.random.rand(len(positive_files), n_cell*n_cell*31)
	#--------------------------------------------------------------------------

	feats_list = []
	for current_image in positive_files:
		img 		= load_image_gray(current_image)
		temp_feat 	= np.expand_dims(vlfeat.hog.hog(img, cell_size).flatten(), axis=0)
		feats_list.append( temp_feat )

	feats = np.concatenate(feats_list, axis=0)
	print("Finished extracting positive HoG features. Shape:", feats.shape)
	
	###########################################################################
	#                             END OF YOUR CODE                            #
	###########################################################################

	return feats

def get_random_negative_features(non_face_scn_path, feature_params, num_samples):
	"""
	This function should return negative training examples (non-faces) from any
	images in 'non_face_scn_path'. Images should be loaded in grayscale because
	the positive training data is only available in grayscale (use
	load_image_gray()).

	Useful functions:
	-   vlfeat.hog.hog(im, cell_size): computes HoG features

	Args:
	-   non_face_scn_path: string. This directory contains many images which
	        have no faces in them.
	-   feature_params: dictionary of HoG feature computation parameters. See
	        the documentation for get_positive_features() for more information.
	-   num_samples: number of negatives to be mined. It is not important for
	        the function to find exactly 'num_samples' non-face features. For
	        example, you might try to sample some number from each image, but
	        some images might be too small to find enough.

	Returns:
	-   N x D matrix where N is the number of non-faces and D is the feature
	        dimensionality, which would be (feature_params['template_size'] /
	        feature_params['hog_cell_size'])^2 * 31 if you're using the default
	        hog parameters.
	"""
	# params for HOG computation
	win_size  		= feature_params.get('template_size', 36)
	cell_size 		= feature_params.get('hog_cell_size', 6)
	negative_files 	= glob(osp.join(non_face_scn_path, '*.jpg'))

	###########################################################################
	#                           TODO: YOUR CODE HERE                          #
	###########################################################################
	
	#---------------- Starter code --------------------------------------------
	# n_cell = np.ceil(win_size/cell_size).astype('int')
	# feats = np.random.rand(len(negative_files), n_cell*n_cell*31)
	#--------------------------------------------------------------------------

	starting_time = time()
	print("using a step size of:", step_size)
	if len(scales) > 1:
		print("Using multiple scales for negative feature extraction. Scales are:", scales)
	else:
		print("Using single scale ... ")

	feats_list = []
	for current_image in negative_files:
		img = load_image_gray(current_image)

		for scale_factor in scales:
		
			sc_r = int(scale_factor * img.shape[0])
			sc_c = int(scale_factor * img.shape[1])

			if sc_r < 36 or sc_c < 36:
				sc_r = 36
				sc_c = 36
				scaled_im = cv2.resize(img, (sc_c, sc_r), interpolation=cv2.INTER_AREA)
				feats_list.append(np.expand_dims(vlfeat.hog.hog(scaled_im, cell_size).flatten(), axis=0))
			else:
				scaled_im = cv2.resize(img, (sc_c, sc_r), interpolation=cv2.INTER_AREA)
				num_steps_rows = (scaled_im.shape[0] - win_size)//step_size
				num_steps_cols = (scaled_im.shape[1] - win_size)//step_size
				for rs in range(num_steps_rows):
					i = rs * step_size
					for cs in range(num_steps_cols):
						j = cs * step_size
						current_patch = scaled_im[i:i+win_size, j:j+win_size]
						feats_list.append(np.expand_dims(vlfeat.hog.hog(current_patch, cell_size).flatten(), axis=0))

	feats_all = np.concatenate(feats_list, axis=0)
	if return_all:
		rand_indxs = np.random.choice(feats_all.shape[0], feats_all.shape[0], replace=False)
	else:
		rand_indxs = np.random.choice(feats_all.shape[0], num_samples, replace=False)
	feats = feats_all[rand_indxs,:]
			
	print("Finished extracting negative HoG features. Shape:", feats.shape)
	print("Time taken:", time() - starting_time)
	
	###########################################################################
	#                             END OF YOUR CODE                            #
	###########################################################################

	return feats

def train_classifier(features_pos, features_neg, C):
	"""
	This function trains a linear SVM classifier on the positive and negative
	features obtained from the previous steps. We fit a model to the features
	and return the svm object.

	Args:
	-   features_pos: N X D array. This contains an array of positive features
	        extracted from get_positive_feats().
	-   features_neg: M X D array. This contains an array of negative features
	        extracted from get_negative_feats().

	Returns:
	-   svm: LinearSVC object. This returns a SVM classifier object trained
	        on the positive and negative features.
	"""
	###########################################################################
	#                           TODO: YOUR CODE HERE                          #
	###########################################################################
	#---------------- Starter code --------------------------------------------
	# svm = PseudoSVM(10,features_pos.shape[1])
	#--------------------------------------------------------------------------
	print("Training linear SVM with positive samples weights of:", pos_ws)
	svm 				= LinearSVC(random_state=0, tol=1e-5, loss='hinge', C=C)
	train_image_feats 	= np.concatenate((features_pos, features_neg), axis=0)
	y 					= np.concatenate((np.ones((features_pos.shape[0],1)), -1.0 * np.ones((features_neg.shape[0],1))), axis=0) 
	Ws 					= np.concatenate( (pos_ws * np.ones((features_pos.shape[0],1)), np.ones((features_neg.shape[0],1))), axis=0) 
	svm.fit(X=train_image_feats, y=np.squeeze(y), sample_weight=np.squeeze(Ws))

	###########################################################################
	#                             END OF YOUR CODE                            #
	###########################################################################

	return svm

def mine_hard_negs(non_face_scn_path, svm, feature_params, conf_thres=-1.0):
	"""
	This function is pretty similar to get_random_negative_features(). The only
	difference is that instead of returning all the extracted features, you only
	return the features with false-positive prediction.

	Useful functions:
	-   vlfeat.hog.hog(im, cell_size): computes HoG features
	-   svm.predict(feat): predict features

	Args:
	-   non_face_scn_path: string. This directory contains many images which
	        have no faces in them.
	-   feature_params: dictionary of HoG feature computation parameters. See
	        the documentation for get_positive_features() for more information.
	-   svm: LinearSVC object

	Returns:
	-   N x D matrix where N is the number of non-faces which are
	        false-positive and D is the feature dimensionality.
	"""

	# params for HOG computation
	win_size = feature_params.get('template_size', 36)
	cell_size = feature_params.get('hog_cell_size', 6)

	negative_files = glob(osp.join(non_face_scn_path, '*.jpg'))
	
	print("Mining for hard negs using a step size of:", step_size, "and confidence threshold of:", conf_thres)
	if len(scales) > 1:
		print("Using multiple scales for negative feature extraction. Scales are:", scales)
	else:
		print("Using single scale ... ")

	###########################################################################
	#                           TODO: YOUR CODE HERE                          #
	###########################################################################
	
	W = svm.coef_ # (1, 1116)
	b = svm.intercept_ # (1,)
	
	#---------------- Starter code --------------------------------------------
	# n_cell = np.ceil(win_size/cell_size).astype('int')
	# feats = np.random.rand(len(negative_files), n_cell*n_cell*31)
	#--------------------------------------------------------------------------
	starting_time = time()
	feats_list = []
	for current_image in negative_files:
		img = load_image_gray(current_image)

		for scale_factor in scales:
		
			sc_r = int(scale_factor * img.shape[0])
			sc_c = int(scale_factor * img.shape[1])

			if sc_r < 36 or sc_c < 36:
				sc_r = 36
				sc_c = 36
				scaled_im = cv2.resize(img, (sc_c, sc_r), interpolation=cv2.INTER_AREA)
				curr_window_feat = np.expand_dims(vlfeat.hog.hog(scaled_im, cell_size).flatten(), axis=-1)
				pred_conf = W.dot(curr_window_feat) + b
				if pred_conf >= conf_thres:
					feats_list.append(curr_window_feat)
			else:
				scaled_im = cv2.resize(img, (sc_c, sc_r), interpolation=cv2.INTER_AREA)
				num_steps_rows = (scaled_im.shape[0] - win_size)//step_size
				num_steps_cols = (scaled_im.shape[1] - win_size)//step_size
				for rs in range(num_steps_rows):
					i = rs * step_size
					for cs in range(num_steps_cols):
						j = cs * step_size				
						current_patch = scaled_im[i:i+win_size, j:j+win_size]
						curr_window_feat = np.expand_dims(vlfeat.hog.hog(current_patch, cell_size).flatten(), axis=-1)
						pred_conf = W.dot(curr_window_feat) + b
						if pred_conf >= conf_thres:
							feats_list.append(curr_window_feat)

	feats = np.concatenate(feats_list, axis=-1).T
	print(feats.shape)
	print("Time taken:", time() - starting_time)
	###########################################################################
	#                             END OF YOUR CODE                            #
	###########################################################################

	return feats

def run_detector(test_scn_path, svm, feature_params, verbose=False, conf_thres=-1.0):
	"""
	This function returns detections on all of the images in a given path. You
	will want to use non-maximum suppression on your detections or your
	performance will be poor (the evaluation counts a duplicate detection as
	wrong). The non-maximum suppression is done on a per-image basis. The
	starter code includes a call to a provided non-max suppression function.

	The placeholder version of this code will return random bounding boxes in
	each test image. It will even do non-maximum suppression on the random
	bounding boxes to give you an example of how to call the function.

	Your actual code should convert each test image to HoG feature space with
	a _single_ call to vlfeat.hog.hog() for each scale. Then step over the HoG
	cells, taking groups of cells that are the same size as your learned
	template, and classifying them. If the classification is above some
	confidence, keep the detection and then pass all the detections for an
	image to non-maximum suppression. For your initial debugging, you can
	operate only at a single scale and you can skip calling non-maximum
	suppression. Err on the side of having a low confidence threshold (even
	less than zero) to achieve high enough recall.

	Args:
	-   test_scn_path: (string) This directory contains images which may or
	        may not have faces in them. This function should work for the
	        MIT+CMU test set but also for any other images (e.g. class photos).
	-   svm: A trained sklearn.svm.LinearSVC object
	-   feature_params: dictionary of HoG feature computation parameters.
	    You can include various parameters in it. Two defaults are:
	        -   template_size: (default 36) The number of pixels spanned by
	        each train/test template.
	        -   hog_cell_size: (default 6) The number of pixels in each HoG
	        cell. template size should be evenly divisible by hog_cell_size.
	        Smaller HoG cell sizes tend to work better, but they make things
	        slowerbecause the feature dimensionality increases and more
	        importantly the step size of the classifier decreases at test time.
	-   verbose: prints out debug information if True

	Returns:
	-   bboxes: N x 4 numpy array. N is the number of detections.
	        bboxes(i,:) is [x_min, y_min, x_max, y_max] for detection i.
	-   confidences: (N, ) size numpy array. confidences(i) is the real-valued
	        confidence of detection i.
	-   image_ids: List with N elements. image_ids[i] is the image file name
	        for detection i. (not the full path, just 'albert.jpg')
	"""
	im_filenames = sorted(glob(osp.join(test_scn_path, '*.jpg')))
	bboxes = np.empty((0, 4))
	confidences = np.empty(0)
	image_ids = []

	# number of top detections to feed to NMS
	topk = 15

	# params for HOG computation
	win_size = feature_params.get('template_size', 36)
	cell_size = feature_params.get('hog_cell_size', 6)
	# scale_factor = feature_params.get('scale_factor', 0.7)
	template_size = int(win_size / cell_size)

	W = svm.coef_ # (1, 1116)
	b = svm.intercept_ # (1,)

	if len(detection_scales)>1:
		print("Detecting faces at multiple scales of:", detection_scales,"\n")
	print("Running detector with step size of:", detect_step_size,"and confidence threshold of:", conf_thres,"\n")
	starting_time = time()

	for idx, im_filename in enumerate(im_filenames):
		print('Detecting faces in {:s}'.format(im_filename))
		im = load_image_gray(im_filename)
		im_id = osp.split(im_filename)[-1]
		im_shape = im.shape
		# create scale space HOG pyramid and return scores for prediction

		#######################################################################
		#                        TODO: YOUR CODE HERE                         #
		#######################################################################

		#---------------- Starter code --------------------------------------------
		# cur_x_min = (np.random.rand(15,1) * im_shape[1]).astype('int')
		# cur_y_min = (np.random.rand(15,1) * im_shape[0]).astype('int')
		# cur_bboxes = np.hstack([cur_x_min, cur_y_min, \
		#     (cur_x_min + np.random.rand(15,1)*50).astype('int'), \
		#     (cur_y_min + np.random.rand(15,1)*50).astype('int')])
		# cur_confidences = np.random.rand(15)*4 - 2
		#--------------------------------------------------------------------------
		
		cur_bboxes = []
		cur_confidences = []
		for scale_factor in detection_scales:

			sc_r = int(scale_factor * im_shape[0])
			sc_c = int(scale_factor * im_shape[1])

			scaled_im = cv2.resize(im, (sc_c, sc_r), interpolation=cv2.INTER_AREA)
			num_steps_rows = (scaled_im.shape[0] - win_size)//detect_step_size
			num_steps_cols = (scaled_im.shape[1] - win_size)//detect_step_size

			for rs in range(num_steps_rows):
				i = rs * detect_step_size
				for cs in range(num_steps_cols):
					j = cs * detect_step_size				
					current_patch = scaled_im[i:i+win_size, j:j+win_size]
					curr_window_feat = np.expand_dims(vlfeat.hog.hog(current_patch, cell_size).flatten(), axis=-1)
					pred_conf = W.dot(curr_window_feat) + b
					if pred_conf >= conf_thres:
						cur_confidences.append(pred_conf)
						cur_bboxes.append( np.expand_dims( (1.0/scale_factor) * np.array([j, i, j+win_size, i+win_size]).astype(np.float32), axis=0)) 
						cur_bboxes[-1] = cur_bboxes[-1].astype(int)	

		num_detections = len(cur_confidences)		
		# print("Number of faces detected:", num_detections)	
		if num_detections > 1:
			cur_confidences = np.squeeze(np.concatenate(cur_confidences, 0))
			cur_bboxes		= np.concatenate(cur_bboxes, axis=0)
		elif num_detections == 1:
			cur_confidences = np.squeeze(cur_confidences[-1], axis=-1)
			cur_bboxes		= cur_bboxes[-1]	

		#######################################################################
		#                          END OF YOUR CODE                           #
		#######################################################################

		### non-maximum suppression ###
		# non_max_supr_bbox() can actually get somewhat slow with thousands of
		# initial detections. You could pre-filter the detections by confidence,
		# e.g. a detection with confidence -1.1 will probably never be
		# meaningful. You probably _don't_ want to threshold at 0.0, though. You
		# can get higher recall with a lower threshold. You should not modify
		# anything in non_max_supr_bbox(). If you want to try your own NMS methods,
		# please create another function.
		if num_detections > 0:	

			idsort = np.argsort(-cur_confidences)[:topk]
			cur_bboxes = cur_bboxes[idsort]
			cur_confidences = cur_confidences[idsort]

			is_valid_bbox = non_max_suppression_bbox(cur_bboxes, cur_confidences,
			    im_shape, verbose=verbose)

			print('NMS done, {:d} detections passed'.format(sum(is_valid_bbox)))
			cur_bboxes = cur_bboxes[is_valid_bbox]
			cur_confidences = cur_confidences[is_valid_bbox]
	
			bboxes = np.vstack((bboxes, cur_bboxes))
			confidences = np.hstack((confidences, cur_confidences))
			image_ids.extend([im_id] * len(cur_confidences))

	print("Time taken:", time() - starting_time)

	return bboxes, confidences, image_ids




